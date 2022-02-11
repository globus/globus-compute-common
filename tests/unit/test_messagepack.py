import json
import logging
import uuid

import pydantic
import pytest

from funcx_common.messagepack import MessagePacker, UnrecognizedProtocolVersion
from funcx_common.messagepack.message_types import (
    EPStatusReport,
    ManagerStatusReport,
    Result,
    ResultErrorCode,
    ResultErrorDetails,
    Task,
)
from funcx_common.messagepack.message_types.base import Message, meta

ID_ZERO = uuid.UUID(int=0)


def crudely_pack_data(data):
    return b"\x01" + json.dumps(data, separators=(",", ":")).encode()


@pytest.fixture
def v1_packer():
    return MessagePacker(default_protocol_version=1)


@pytest.mark.parametrize(
    "message_class, init_args, expect_values",
    [
        (
            EPStatusReport,
            {
                "endpoint_id": uuid.UUID("058cf505-a09e-4af3-a5f2-eb2e931af141"),
                "ep_status_report": {},
                "task_statuses": {},
            },
            None,
        ),
        (
            EPStatusReport,
            {"endpoint_id": ID_ZERO, "ep_status_report": {}, "task_statuses": {}},
            None,
        ),
        (ManagerStatusReport, {"task_statuses": {}}, None),
        (
            ManagerStatusReport,
            {"task_statuses": {"foo": [ID_ZERO, "abc"]}},
            {"task_statuses": {"foo": [str(ID_ZERO), "abc"]}},
        ),
        (
            Task,
            {
                "task_id": uuid.UUID("058cf505-a09e-4af3-a5f2-eb2e931af141"),
                "container_id": uuid.UUID("f72b4570-8273-4913-a6a0-d77af864beb1"),
                "task_buffer": "foo data",
            },
            None,
        ),
        (
            Result,
            {
                "task_id": ID_ZERO,
                "data": "foo-bar-baz",
                "error_details": None,
            },
            None,
        ),
        (
            Result,
            {  # as JSON data
                "task_id": str(ID_ZERO),
                "data": "foo-bar-baz",
                "error_details": {
                    "is_system_error": True,
                    "code": "ManagerLost",
                    "user_message": "something bad happened",
                },
            },
            {  # result has native types
                "task_id": ID_ZERO,
                "data": "foo-bar-baz",
                "error_details": ResultErrorDetails(
                    is_system_error=True,
                    code=ResultErrorCode.ManagerLost,
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
                    is_system_error=True,
                    code=ResultErrorCode.ManagerLost,
                    user_message="something bad happened",
                ),
            },
            None,  # result is identical
        ),
    ],
)
def test_pack_and_unpack_v1(v1_packer, message_class, init_args, expect_values):
    if expect_values is None:
        expect_values = init_args

    message_obj = message_class(**init_args)

    on_wire = v1_packer.pack(message_obj)
    # first byte (version byte) "1"
    assert on_wire[0:1] == b"\x01"
    # body is JSON, and valid
    payload = json.loads(on_wire[1:])
    assert "message_type" in payload
    assert "data" in payload

    message_obj2 = v1_packer.unpack(on_wire)
    assert isinstance(message_obj2, message_class)
    for k, v in expect_values.items():
        assert hasattr(message_obj2, k)
        v2 = getattr(message_obj2, k)
        assert v2 == v
        # explicitly check that the types of the two values match
        # otherwise, you get a false-negative when comparing `{"foo": "bar"}` to a
        # pydantic model object which `dict`s into `{"foo": "bar"}`
        assert type(v2) == type(v)


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
        # EPStatusReport requires: endpoint_id, ep_status_report, task_statuses
        (EPStatusReport, {"ep_status_report": {}, "task_statuses": {}}),
        (EPStatusReport, {"endpoint_id": ID_ZERO, "task_statuses": {}}),
        (EPStatusReport, {"endpoint_id": ID_ZERO, "ep_status_report": {}}),
        # ManagerStatusReport requires: task_statuses
        (ManagerStatusReport, {}),
        # Task requires: task_id, container_id, task_buffer
        (Task, {"container_id": ID_ZERO, "task_buffer": "foo data"}),
        (Task, {"task_id": ID_ZERO, "task_buffer": "foo data"}),
        (Task, {"task_id": ID_ZERO, "container_id": ID_ZERO}),
        # Result requires: task_id, data
        (Result, {"data": "foo-bar-baz", "error_details": None}),
        (Result, {"task_id": ID_ZERO, "error_details": None}),
        # if Result.error_details is not null, it requires:
        #   is_system_error, code, user_message
        (
            Result,
            {
                "task_id": ID_ZERO,
                "data": "foo-bar-baz",
                "error_details": {
                    "code": "ManagerLost",
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
                    "is_system_error": True,
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
                    "is_system_error": True,
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


@pytest.mark.parametrize("code_val", list(ResultErrorCode))
def test_result_error_details_accepts_valid_codes(code_val):
    val = ResultErrorDetails(is_system_error=True, user_message="foo", code=code_val)
    # confirm that strings get converted under parse_obj
    val2 = ResultErrorDetails.parse_obj(
        dict(is_system_error=True, user_message="foo", code=code_val.value)
    )
    assert val == val2


def test_result_error_details_rejects_unknown_codes():
    with pytest.raises(pydantic.ValidationError):
        ResultErrorDetails(
            is_system_error=True, user_message="foo", code="FOO BAR UNKNOWN"
        )


@pytest.mark.parametrize(
    "details, expect",
    [
        (None, False),
        (
            ResultErrorDetails(
                is_system_error=False,
                user_message="foo",
                code=ResultErrorCode.ContainerError,
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


def test_invalid_uuid_rejected_on_unpack(v1_packer):
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
    v1_packer.unpack(buf_valid)

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
        v1_packer.unpack(buf_invalid)


def test_cannot_unpack_unknown_message_type(v1_packer):
    buf = crudely_pack_data({"message_type": "foo", "data": {}})
    with pytest.raises(pydantic.ValidationError):
        v1_packer.unpack(buf)


def test_cannot_unpack_message_missing_data(v1_packer):
    buf = crudely_pack_data({"message_type": "task"})
    with pytest.raises(pydantic.ValidationError):
        v1_packer.unpack(buf)


def test_cannot_unpack_message_missing_type(v1_packer):
    buf = crudely_pack_data({"data": {}})
    with pytest.raises(pydantic.ValidationError):
        v1_packer.unpack(buf)


def test_cannot_unpack_message_empty_data(v1_packer):
    buf = crudely_pack_data({"message_type": "task", "data": {}})
    with pytest.raises(pydantic.ValidationError):
        v1_packer.unpack(buf)


@pytest.mark.parametrize(
    "payload, expect_err",
    [
        ([{"message_type": "task"}], "expected dict not list"),
        ({"message_type": ["task"], "data": {}}, "str type expected"),
        ({"message_type": "task", "data": None}, "none is not an allowed value"),
    ],
)
def test_cannot_unpack_message_wrong_type(v1_packer, payload, expect_err):
    buf = crudely_pack_data(payload)
    with pytest.raises(pydantic.ValidationError) as excinfo:
        v1_packer.unpack(buf)
    assert expect_err in str(excinfo.value)


def test_cannot_unpack_unrecognized_protocol_version(v1_packer):
    buf = crudely_pack_data({"message_type": "foo", "data": {}})
    buf = b"\x02" + buf[1:]
    with pytest.raises(UnrecognizedProtocolVersion):
        v1_packer.unpack(buf)


def test_failure_on_empty_buffer(v1_packer):
    with pytest.raises(ValueError):
        v1_packer.unpack(b"")


def test_unknown_data_fields_warn(v1_packer, caplog):
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
    with caplog.at_level(logging.WARNING, logger="funcx_common"):
        msg = v1_packer.unpack(buf)
        # successfully unpacked
        assert isinstance(msg, Task)
    # but logged a warning (do two assertions so as not to insist on a precise format
    # for the logged fields
    assert (
        "encountered unknown data fields while reading a task message:"
    ) in caplog.text
    assert "foo_field" in caplog.text


def test_unknown_envelope_fields_warn(v1_packer, caplog):
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
    with caplog.at_level(logging.WARNING, logger="funcx_common"):
        msg = v1_packer.unpack(buf)
        # successfully unpacked
        assert isinstance(msg, Task)
    # but logged a warning (do two assertions so as not to insist on a precise format
    # for the logged fields
    assert (
        "encountered unknown envelope fields while reading a task message:"
    ) in caplog.text
    assert "unexpected_fieldname" in caplog.text


def test_meta_decorator():
    # case 1: no defined internal Meta (inherited from Message)
    @meta(foo=1, bar=2)
    class MyMessage(Message):
        ...

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
        ...

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
