import json
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
    # second byte (reserved byte) "0"
    assert on_wire[1:2] == b"\x00"
    # body is JSON, and valid
    payload = json.loads(on_wire[2:])
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
    buf = b'\x01\x00{"message_type":"foo","data":{}}'
    with pytest.raises(UnrecognizedMessageTypeError):
        v1_packer.unpack(buf)


def test_cannot_unpack_message_missing_data(v1_packer):
    buf = b'\x01\x00{"message_type":"task"}'
    with pytest.raises(InvalidMessagePayloadError):
        v1_packer.unpack(buf)


def test_cannot_unpack_message_missing_type(v1_packer):
    buf = b'\x01\x00{"data":{}}'
    with pytest.raises(InvalidMessagePayloadError):
        v1_packer.unpack(buf)


def test_cannot_unpack_message_empty_data(v1_packer):
    buf = b'\x01\x00{"message_type":"task","data":{}}'
    with pytest.raises(InvalidMessagePayloadError):
        v1_packer.unpack(buf)


def test_cannot_unpack_unrecognized_protocol_version(v1_packer):
    buf = b'\x02\x00{"message_type":"foo","data":{}}'
    with pytest.raises(UnrecognizedProtocolVersion):
        v1_packer.unpack(buf)


def test_failure_on_empty_buffer(v1_packer):
    with pytest.raises(ValueError):
        v1_packer.unpack(b"")
