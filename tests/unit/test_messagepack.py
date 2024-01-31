import json
import logging
import typing as t
import uuid

import pydantic
import pytest

from globus_compute_common.messagepack import (
    MessagePacker,
    UnrecognizedProtocolVersion,
    WrongMessageTypeError,
    pack,
    unpack,
)
from globus_compute_common.messagepack.message_types import (
    Container,
    EPStatusReport,
    ManagerStatusReport,
    Result,
    ResultErrorDetails,
    Task,
    TaskCancel,
    TaskTransition,
)
from globus_compute_common.messagepack.message_types.base import Message, meta
from globus_compute_common.messagepack.protocol_versions.proto1 import (
    MessageEnvelope,
    _load,
)
from globus_compute_common.tasks.constants import ActorName, TaskState

ID_ZERO = uuid.UUID(int=0)


@meta(message_type="result")
class ResultV1(Message):
    """
    Old Result before 'details' field was added, for backwards compatibility
    testing
    """

    task_id: uuid.UUID
    data: str
    error_details: t.Optional[ResultErrorDetails]
    task_statuses: t.Optional[t.List[TaskTransition]]

    @property
    def is_error(self) -> bool:
        return self.error_details is not None


def crudely_pack_data(data):
    return b"\x01" + json.dumps(data, separators=(",", ":")).encode()


@pytest.mark.parametrize(
    "message_class, init_args, expect_values",
    [
        (
            EPStatusReport,
            {
                "endpoint_id": uuid.UUID("058cf505-a09e-4af3-a5f2-eb2e931af141"),
                "global_state": {},
                "task_statuses": {},
            },
            None,
        ),
        (
            EPStatusReport,
            {"endpoint_id": ID_ZERO, "global_state": {}, "task_statuses": {}},
            None,
        ),
        (
            EPStatusReport,
            {
                "endpoint_id": ID_ZERO,
                "global_state": {
                    str(ID_ZERO): [
                        TaskTransition(
                            timestamp=1,
                            state=TaskState.EXEC_END,
                            actor=ActorName.INTERCHANGE,
                        )
                    ]
                },
                "task_statuses": {},
            },
            None,
        ),
        (
            EPStatusReport,
            {
                "endpoint_id": ID_ZERO,
                "global_state": {},
                "task_statuses": {
                    str(ID_ZERO): [
                        TaskTransition(
                            timestamp=1,
                            state=TaskState.EXEC_END,
                            actor=ActorName.INTERCHANGE,
                        )
                    ]
                },
            },
            None,
        ),
        (  # ep_status_report is an alias for global_state
            EPStatusReport,
            {"endpoint_id": ID_ZERO, "ep_status_report": {}, "task_statuses": {}},
            {"endpoint_id": ID_ZERO, "global_state": {}, "task_statuses": {}},
        ),
        (ManagerStatusReport, {"task_statuses": {}}, None),
        (
            ManagerStatusReport,
            {
                "task_statuses": {
                    "foo": [
                        TaskTransition(
                            timestamp=1,
                            state=TaskState.EXEC_END,
                            actor=ActorName.INTERCHANGE,
                        )
                    ]
                }
            },
            None,
        ),
        (
            Container,
            {"container_id": uuid.uuid4(), "name": "some container name", "images": []},
            None,
        ),
        (
            Task,
            {
                "task_id": uuid.UUID("058cf505-a09e-4af3-a5f2-eb2e931af141"),
                "container": Container(
                    container_id=uuid.UUID("f72b4570-8273-4913-a6a0-d77af864beb1"),
                    name="Some Container",
                    images=[],
                ),
                "task_buffer": "foo data",
            },
            None,
        ),
        (
            Task,
            {
                "task_id": uuid.UUID("058cf505-a09e-4af3-a5f2-eb2e931af141"),
                "container": None,
                "task_buffer": "foo data",
            },
            None,
        ),
        (
            Task,
            {
                "task_id": uuid.UUID("058cf505-a09e-4af3-a5f2-eb2e931af141"),
                "task_buffer": "foo data",
            },
            None,
        ),
        (TaskCancel, {"task_id": ID_ZERO}, None),
        (
            Result,
            {
                "task_id": ID_ZERO,
                "data": "foo-bar-baz",
                "error_details": None,
            },
            None,
        ),
        (  # "error_details" gets populated even if it was not originally set
            Result,
            {"task_id": ID_ZERO, "data": "foo-bar-baz"},
            {
                "task_id": ID_ZERO,
                "data": "foo-bar-baz",
                "error_details": None,
            },
        ),
        (
            Result,
            {  # as JSON data
                "task_id": str(ID_ZERO),
                "data": "foo-bar-baz",
                "error_details": {
                    "code": "ManagerLost",
                    "user_message": "something bad happened",
                },
            },
            {  # result has native types
                "task_id": ID_ZERO,
                "data": "foo-bar-baz",
                "error_details": ResultErrorDetails(
                    code="ManagerLost",
                    user_message="something bad happened",
                ),
            },
        ),
        (
            Result,
            {  # as native types
                "task_id": ID_ZERO,
                "data": "foo-bar-baz",
                "error_details": ResultErrorDetails(
                    code="ManagerLost",
                    user_message="something bad happened",
                ),
            },
            None,  # result is identical
        ),
        (
            TaskTransition,
            {
                "timestamp": 1,
                "actor": ActorName.WORKER,
                "state": TaskState.SUCCESS,
            },
            None,
        ),
    ],
)
@pytest.mark.parametrize("protocol_version", [None, 1])
def test_pack_and_unpack(message_class, init_args, expect_values, protocol_version):
    if protocol_version is None:
        do_pack = pack
        do_unpack = unpack
    else:
        packer = MessagePacker(default_protocol_version=protocol_version)
        do_pack = packer.pack
        do_unpack = packer.unpack

    if expect_values is None:
        expect_values = init_args

    message_obj = message_class(**init_args)

    on_wire = do_pack(message_obj)
    # first byte (version byte)
    if protocol_version is not None:
        # 1 -> b"\x01" , and so forth
        assert on_wire[0:1] == chr(protocol_version).encode()
    # body is JSON, and valid
    payload = json.loads(on_wire[1:])
    assert "message_type" in payload
    assert "data" in payload

    message_obj2 = do_unpack(on_wire)
    assert isinstance(message_obj2, message_class)
    for k, v in expect_values.items():
        assert hasattr(message_obj2, k)
        v2 = getattr(message_obj2, k)
        assert v2 == v
        # explicitly check that the types of the two values match
        # otherwise, you get a false-negative when comparing `{"foo": "bar"}` to a
        # pydantic model object which `dict`s into `{"foo": "bar"}`
        assert type(v2) == type(v)  # noqa: E721


@pytest.mark.parametrize(
    "orig_class, new_class, init_args, expect_values",
    [
        (
            # New version of Result will be deserialized by old unpack
            Result,
            ResultV1,
            {
                "task_id": ID_ZERO,
                "data": "foo-bar-baz",
                "metadata": {"a": "b"},
            },
            {
                "task_id": ID_ZERO,
                "data": "foo-bar-baz",
            },
        ),
        (
            # Old version of Result will be deserialized by new unpack
            ResultV1,
            Result,
            {
                "task_id": ID_ZERO,
                "data": "d",
                "error_details": ResultErrorDetails(code="c", user_message="m"),
            },
            {
                "task_id": ID_ZERO,
                "data": "d",
                "edcode": "c",
            },
        ),
        (
            # Pre-serialized old version of Result is unpacked correctly
            None,
            Result,
            b'\x01{"message_type":"result","data":{"task_id":"00000000-0000-0000-0000-000000000000","data":"d","error_details":{"code":"c","user_message":"m"},"task_statuses":null}}',  # noqa: E501
            {
                "task_id": ID_ZERO,
                "data": "d",
                "edcode": "c",
            },
        ),
    ],
)
def test_result_back_compat(orig_class, new_class, init_args, expect_values):
    packer = MessagePacker(default_protocol_version=1)
    do_pack = packer.pack

    def test_unpack(buf: bytes, force_class) -> Message:
        body = buf[1:]
        payload = json.loads(body)
        envelope = _load(MessageEnvelope, payload)
        return _load(force_class, envelope.data)

    do_unpack = test_unpack

    if orig_class is None:
        on_wire = init_args
    else:
        message_obj = orig_class(**init_args)
        on_wire = do_pack(message_obj)

    unpacked_msg = do_unpack(on_wire, new_class)

    assert isinstance(unpacked_msg, new_class)
    assert unpacked_msg.task_id == expect_values["task_id"]
    assert unpacked_msg.data == expect_values["data"]
    if "edcode" in expect_values:
        assert unpacked_msg.error_details.code == expect_values["edcode"]

    # Either the new Result's metadata is discarded when serialized
    #  by old package, or old Result is deserialized into a new one
    #  without the info
    if "metadata" not in expect_values:
        assert not hasattr(unpacked_msg, "metadata")


def _required_arg_test_ids(param):
    if isinstance(param, type):
        return param.__name__
    elif isinstance(param, dict):
        return "/".join(param.keys())
    else:
        raise NotImplementedError


@pytest.mark.parametrize(
    "message_class, init_args",
    [
        # EPStatusReport requires:
        #   endpoint_id, global_state OR ep_status_report, task_statuses
        (EPStatusReport, {"global_state": {}, "task_statuses": {}}),
        (EPStatusReport, {"ep_status_report": {}, "task_statuses": {}}),
        (EPStatusReport, {"endpoint_id": ID_ZERO, "task_statuses": {}}),
        (EPStatusReport, {"endpoint_id": ID_ZERO, "global_state": {}}),
        (EPStatusReport, {"endpoint_id": ID_ZERO, "ep_status_report": {}}),
        # ManagerStatusReport requires: task_statuses
        (ManagerStatusReport, {}),
        # Task requires: task_id, task_buffer
        (Task, {"container_id": ID_ZERO, "task_buffer": "foo data"}),
        (Task, {"task_id": ID_ZERO, "container_id": ID_ZERO}),
        # TaskCancel requires: task_id
        (TaskCancel, {}),
        # Result requires: task_id, data
        (Result, {"data": "foo-bar-baz", "error_details": None}),
        (Result, {"task_id": ID_ZERO, "error_details": None}),
        # if Result.error_details is not null, it requires:
        #   code, user_message
        (
            Result,
            {
                "task_id": ID_ZERO,
                "data": "foo-bar-baz",
                "error_details": {
                    "user_message": "something bad happened",
                },
            },
        ),
        (
            Result,
            {
                "task_id": ID_ZERO,
                "data": "foo-bar-baz",
                "error_details": {
                    "code": "ManagerLost",
                },
            },
        ),
    ],
    ids=_required_arg_test_ids,
)
def test_message_missing_required_fields(message_class, init_args):
    with pytest.raises(pydantic.ValidationError):
        message_class(**init_args)


@pytest.mark.parametrize(
    "details, expect",
    [
        (None, False),
        (
            ResultErrorDetails(
                user_message="foo",
                code="ContainerError",
            ),
            True,
        ),
    ],
)
def test_result_is_error(details, expect):
    val = Result(task_id=ID_ZERO, data="foo", error_details=details)
    assert val.is_error is expect


def test_invalid_uuid_rejected_on_init():
    Task(task_id=ID_ZERO, container_id=ID_ZERO, task_buffer="foo")
    with pytest.raises(pydantic.ValidationError):
        Task(task_id="foo", container_id=ID_ZERO, task_buffer="foo")


def test_invalid_uuid_rejected_on_unpack():
    buf_valid = crudely_pack_data(
        {
            "message_type": "task",
            "data": {
                "task_id": str(ID_ZERO),
                "container_id": str(ID_ZERO),
                "task_buffer": "foo",
            },
        }
    )
    unpack(buf_valid)

    buf_invalid = crudely_pack_data(
        {
            "message_type": "task",
            "data": {
                "task_id": "foo",
                "container_id": str(ID_ZERO),
                "task_buffer": "foo",
            },
        }
    )
    with pytest.raises(pydantic.ValidationError):
        unpack(buf_invalid)


def test_cannot_unpack_unknown_message_type():
    buf = crudely_pack_data({"message_type": "foo", "data": {}})
    with pytest.raises(pydantic.ValidationError):
        unpack(buf)


def test_cannot_unpack_message_missing_data():
    buf = crudely_pack_data({"message_type": "task"})
    with pytest.raises(pydantic.ValidationError):
        unpack(buf)


def test_cannot_unpack_message_missing_type():
    buf = crudely_pack_data({"data": {}})
    with pytest.raises(pydantic.ValidationError):
        unpack(buf)


def test_cannot_unpack_message_empty_data():
    buf = crudely_pack_data({"message_type": "task", "data": {}})
    with pytest.raises(pydantic.ValidationError):
        unpack(buf)


@pytest.mark.parametrize(
    "payload, expect_err",
    [
        ([{"message_type": "task"}], "expected dict not list"),
        ({"message_type": ["task"], "data": {}}, "str type expected"),
        ({"message_type": "task", "data": None}, "none is not an allowed value"),
    ],
)
def test_cannot_unpack_message_wrong_type(payload, expect_err):
    buf = crudely_pack_data(payload)
    with pytest.raises(pydantic.ValidationError) as excinfo:
        unpack(buf)
    assert expect_err in str(excinfo.value)


def test_cannot_unpack_unrecognized_protocol_version():
    buf = crudely_pack_data({"message_type": "foo", "data": {}})
    buf = b"\x02" + buf[1:]
    with pytest.raises(UnrecognizedProtocolVersion):
        unpack(buf)


def test_failure_on_empty_buffer():
    with pytest.raises(ValueError):
        unpack(b"")


def test_unknown_data_fields_warn(caplog):
    buf = crudely_pack_data(
        {
            "message_type": "task",
            "data": {
                "task_id": str(ID_ZERO),
                "container_id": str(ID_ZERO),
                "task_buffer": "foo",
                "foo_field": "bar",
            },
        }
    )
    with caplog.at_level(logging.WARNING, logger="globus_compute_common"):
        msg = unpack(buf)
        # successfully unpacked
        assert isinstance(msg, Task)
    # but logged a warning (do two assertions so as not to insist on a precise format
    # for the logged fields)
    assert (
        "encountered unknown data fields while reading a task message:"
    ) in caplog.text
    assert "foo_field" in caplog.text


def test_dont_warn_alias_fields(caplog):
    buf = crudely_pack_data(
        {
            "message_type": "ep_status_report",
            "data": {
                "endpoint_id": str(ID_ZERO),
                "ep_status_report": {"this is an alias": "for global_state"},
                "task_statuses": [],
            },
        }
    )
    with caplog.at_level(logging.WARNING, logger="globus_compute_common"):
        msg = unpack(buf)
        # successfully unpacked
        assert isinstance(msg, EPStatusReport)
    # but logged no warning (do two assertions so as not to insist on a precise format
    # for the logged fields)
    assert "encountered unknown data fields" not in caplog.text
    assert "ep_status_report" not in caplog.text


def test_unknown_envelope_fields_warn(caplog):
    buf = crudely_pack_data(
        {
            "message_type": "task",
            "data": {
                "task_id": str(ID_ZERO),
                "container_id": str(ID_ZERO),
                "task_buffer": "foo",
            },
            "unexpected_fieldname": "foo",
        }
    )
    with caplog.at_level(logging.WARNING, logger="globus_compute_common"):
        msg = unpack(buf)
        # successfully unpacked
        assert isinstance(msg, Task)
    # but logged a warning (do two assertions so as not to insist on a precise format
    # for the logged fields)
    assert (
        "encountered unknown envelope fields while reading a task message:"
    ) in caplog.text
    assert "unexpected_fieldname" in caplog.text


def test_meta_decorator():
    # case 1: no defined internal Meta (inherited from Message)
    @meta(foo=1, bar=2)
    class MyMessage(Message):
        pass

    assert MyMessage.Meta.foo == 1
    assert MyMessage.Meta.bar == 2
    # inherited Meta was not modified
    assert not hasattr(Message.Meta, "foo")
    assert not hasattr(Message.Meta, "bar")

    # case 2: defined internal Meta, mixed with decorator values
    @meta(foo=1)
    class MyMessage2(Message):
        class Meta:
            bar = 3

    assert MyMessage2.Meta.foo == 1
    assert MyMessage2.Meta.bar == 3

    # case 3: inherited internal Meta from non-Message class
    @meta(message_type="foo")
    class MyMessage3(MyMessage2):
        pass

    assert MyMessage3.Meta.foo == 1
    assert MyMessage3.Meta.bar == 3
    assert MyMessage3.Meta.message_type == "foo"

    # case 4: class which does not define a Meta dict at all
    # (does not inherit from Message)
    @meta(foo=1)
    class MyMessage4:
        pass

    assert hasattr(MyMessage4, "Meta")
    assert MyMessage4.Meta.foo == 1


def test_messages_can_assert_type():
    message = Task(task_id=ID_ZERO, container_id=ID_ZERO, task_buffer="foo")
    # ok cases
    message.assert_one_of_types(Task)
    message.assert_one_of_types(Task, Result)
    message.assert_one_of_types(Result, Task, EPStatusReport)

    # failing cases
    with pytest.raises(WrongMessageTypeError):
        message.assert_one_of_types(Result, EPStatusReport)
    with pytest.raises(WrongMessageTypeError):
        message.assert_one_of_types()
