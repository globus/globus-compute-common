import json
import logging
import uuid

import pytest

from funcx_common.messagepack import (
    InvalidMessagePayloadError,
    MessagePacker,
    UnrecognizedMessageTypeError,
    UnrecognizedProtocolVersion,
)
from funcx_common.messagepack.message_types import (
    EPStatusReport,
    Heartbeat,
    HeartbeatReq,
    ManagerStatusReport,
    ResultsAck,
    Task,
)

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
                "endpoint_id": "058cf505-a09e-4af3-a5f2-eb2e931af141",
                "ep_status_report": {},
                "task_statuses": {},
            },
            None,
        ),
        (
            EPStatusReport,
            {"endpoint_id": ID_ZERO, "ep_status_report": {}, "task_statuses": {}},
            {"endpoint_id": str(ID_ZERO), "ep_status_report": {}, "task_statuses": {}},
        ),
        (Heartbeat, {"endpoint_id": str(ID_ZERO)}, None),
        (HeartbeatReq, {}, None),
        (ManagerStatusReport, {"task_statuses": {}}, None),
        (
            ManagerStatusReport,
            {"task_statuses": {"foo": [ID_ZERO, "abc"]}},
            {"task_statuses": {"foo": [str(ID_ZERO), "abc"]}},
        ),
        (
            ResultsAck,
            {
                "task_id": "058cf505-a09e-4af3-a5f2-eb2e931af141",
            },
            None,
        ),
        (
            Task,
            {
                "task_id": "058cf505-a09e-4af3-a5f2-eb2e931af141",
                "container_id": "f72b4570-8273-4913-a6a0-d77af864beb1",
            },
            None,
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
        assert getattr(message_obj2, k) == v


def test_invalid_uuid_rejected():
    # check that args are correct before checking the value error, to confirm it's a
    # matter of the value for 'task_id'
    Task(task_id=str(ID_ZERO), container_id="f72b4570-8273-4913-a6a0-d77af864beb1")
    with pytest.raises(ValueError):
        Task(task_id="foo", container_id="f72b4570-8273-4913-a6a0-d77af864beb1")


def test_cannot_unpack_unknown_message_type(v1_packer):
    buf = crudely_pack_data({"message_type": "foo", "data": {}})
    with pytest.raises(UnrecognizedMessageTypeError):
        v1_packer.unpack(buf)


def test_cannot_unpack_message_missing_data(v1_packer):
    buf = crudely_pack_data({"message_type": "task"})
    with pytest.raises(InvalidMessagePayloadError):
        v1_packer.unpack(buf)


def test_cannot_unpack_message_missing_type(v1_packer):
    buf = crudely_pack_data({"data": {}})
    with pytest.raises(InvalidMessagePayloadError):
        v1_packer.unpack(buf)


def test_cannot_unpack_message_empty_data(v1_packer):
    buf = crudely_pack_data({"message_type": "task", "data": {}})
    with pytest.raises(InvalidMessagePayloadError):
        v1_packer.unpack(buf)


@pytest.mark.parametrize(
    "payload, expect_err",
    [
        ([{"message_type": "task"}], "non-dict envelope"),
        ({"message_type": ["task"], "data": {}}, "message_type expected str, got list"),
        ({"message_type": "task", "data": None}, "data expected dict, got NoneType"),
    ],
)
def test_cannot_unpack_message_wrong_type(v1_packer, payload, expect_err):
    buf = crudely_pack_data(payload)
    with pytest.raises(InvalidMessagePayloadError) as excinfo:
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
            "message_type": "heartbeat",
            "data": {"endpoint_id": str(ID_ZERO), "foo_field": "bar"},
        }
    )
    with caplog.at_level(logging.WARNING, logger="funcx_common"):
        msg = v1_packer.unpack(buf)
        # successfully unpacked
        assert isinstance(msg, Heartbeat)
    # but logged a warning (do two assertions so as not to insist on a precise format
    # for the logged fields
    assert (
        "encountered unknown data fields while reading a heartbeat message:"
    ) in caplog.text
    assert "foo_field" in caplog.text


def test_unknown_envelope_fields_warn(v1_packer, caplog):
    buf = crudely_pack_data(
        {
            "message_type": "heartbeat",
            "data": {"endpoint_id": str(ID_ZERO)},
            "unexpected_fieldname": "foo",
        }
    )
    with caplog.at_level(logging.WARNING, logger="funcx_common"):
        msg = v1_packer.unpack(buf)
        # successfully unpacked
        assert isinstance(msg, Heartbeat)
    # but logged a warning (do two assertions so as not to insist on a precise format
    # for the logged fields
    assert (
        "encountered unknown envelope fields while reading a heartbeat message:"
    ) in caplog.text
    assert "unexpected_fieldname" in caplog.text
