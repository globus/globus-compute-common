import json
import struct
import uuid

import pytest

from funcx_common.messagepack import (
    InvalidMessagePayloadError,
    Message,
    MessagePacker,
    MessageType,
    UnrecognizedMessageTypeError,
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
def v0_packer():
    return MessagePacker(default_protocol_version=0)


def get_v0_header(m):  # takes Message or MessageType or int
    if isinstance(m, Message):
        m = m.message_type
    if isinstance(m, MessageType):
        m = m.value
    return struct.pack("b", m)


def test_can_manually_v0_get_and_load_heartbeat_req():
    req_obj = HeartbeatReq()
    # body is empty
    assert req_obj.get_v0_body() == b""

    # just ensure that loading does not error; nothing more can be tested here
    HeartbeatReq.load_v0_body(req_obj.get_v0_body())


def test_can_manually_v0_get_and_load_task():
    task_id = str(uuid.uuid1())
    container_id = str(uuid.uuid1())
    task_obj = Task(task_id, container_id, "some data")

    assert task_obj.task_id == task_id
    assert task_obj.container_id == container_id
    assert task_obj.container_id == container_id
    assert task_obj.task_buffer == "some data"

    on_wire = task_obj.get_v0_body()
    assert on_wire == f"TID={task_id};CID={container_id};some data".encode("utf-8")

    task_obj2 = Task.load_v0_body(on_wire)
    assert task_obj2.task_id == task_id
    assert task_obj2.container_id == container_id
    assert task_obj2.task_buffer == "some data"
    assert (
        task_obj2.get_v0_body()
        == f"TID={task_id};CID={container_id};some data".encode("utf-8")
    )


def test_can_pack_and_unpack_task_v0(v0_packer):
    task_id = str(uuid.uuid1())
    container_id = str(uuid.uuid1())
    task_obj = Task(task_id, container_id, "some data")

    on_wire = v0_packer.pack(task_obj)
    payload = f"TID={task_id};CID={container_id};some data".encode("utf-8")
    header = get_v0_header(MessageType.TASK)
    assert on_wire == header + payload

    task_obj2 = v0_packer.unpack(on_wire)
    assert task_obj2.task_id == task_id
    assert task_obj2.container_id == container_id
    assert task_obj2.task_buffer == "some data"


def test_cannot_unpack_unknown_message_type(v0_packer):
    # '100' does not match any real header values
    header = get_v0_header(100)
    payload = b"some message"

    with pytest.raises(UnrecognizedMessageTypeError):
        v0_packer.unpack(header + payload)


# this is the v0 "container_switch_count" encoding
# it's not a complete message; just a valid message fragment for a
# ManagerStatusReport message
VALID_CSC_SEGMENT = (5).to_bytes(10, "little")


@pytest.mark.parametrize(
    "task_statuses",
    [
        {},
        {"foo": "bar"},
        {str(n): {"foo": "bar"} for n in range(1000)},
    ],
)
def test_can_pack_and_unpack_manager_status_report_v0(v0_packer, task_statuses):
    report = ManagerStatusReport(task_statuses, 5)

    task_statuses_s = json.dumps(task_statuses, separators=(",", ":"), sort_keys=True)
    task_statuses_b = task_statuses_s.encode("ascii")

    on_wire = v0_packer.pack(report)
    header = get_v0_header(MessageType.MANAGER_STATUS_REPORT)
    payload = VALID_CSC_SEGMENT + task_statuses_b
    assert on_wire == header + payload

    report2 = v0_packer.unpack(on_wire)
    assert report2.container_switch_count == 5
    assert report2.task_statuses == task_statuses


def test_can_pack_and_unpack_heartbeat_v0(v0_packer):
    hb = Heartbeat(str(ID_ZERO))

    on_wire = v0_packer.pack(hb)
    header = get_v0_header(MessageType.HEARTBEAT)
    payload = str(ID_ZERO).encode("ascii")
    assert on_wire == header + payload

    hb2 = v0_packer.unpack(on_wire)
    assert hb2.endpoint_id == str(ID_ZERO)


@pytest.mark.parametrize(
    "task_statuses",
    [
        {},
        {"foo": "bar"},
        {str(n): {"foo": "bar"} for n in range(1000)},
    ],
)
@pytest.mark.parametrize(
    "ep_status",
    [{}, {"foo": "bar"}],
)
def test_can_pack_and_unpack_ep_status_report_v0(v0_packer, ep_status, task_statuses):
    report = EPStatusReport(str(ID_ZERO), ep_status, task_statuses)

    on_wire = v0_packer.pack(report)
    header = get_v0_header(MessageType.EP_STATUS_REPORT)
    payload = ID_ZERO.bytes + json.dumps(
        [ep_status, task_statuses], separators=(",", ":"), sort_keys=True
    ).encode("ascii")
    assert on_wire == header + payload

    report2 = v0_packer.unpack(on_wire)
    assert report2.endpoint_id == str(ID_ZERO)
    assert report2.ep_status == ep_status
    assert report2.task_statuses == task_statuses


def test_can_pack_and_unpack_resultsack_v0(v0_packer):
    ack = ResultsAck(str(ID_ZERO))

    on_wire = v0_packer.pack(ack)
    header = get_v0_header(MessageType.RESULTS_ACK)
    payload = str(ID_ZERO).encode("ascii")
    assert on_wire == header + payload

    ack2 = v0_packer.unpack(on_wire)
    assert ack2.task_id == str(ID_ZERO)


@pytest.mark.parametrize(
    "message_type, message",
    [
        (MessageType.TASK, b""),
        (MessageType.TASK, b"foo"),
        (MessageType.TASK, b"foo;bar"),
        (MessageType.TASK, b"TID=;CID=;foo"),
        (MessageType.TASK, b";;foo"),
        (MessageType.TASK, f"TID={ID_ZERO};CID=;foo".encode("utf-8")),
        (MessageType.TASK, f"TID=;CID={ID_ZERO};foo".encode("utf-8")),
        (MessageType.TASK, f"TID={ID_ZERO};CID={ID_ZERO}".encode("utf-8")),
        (MessageType.HEARTBEAT, b"foo"),
        (MessageType.MANAGER_STATUS_REPORT, b""),
        (MessageType.MANAGER_STATUS_REPORT, b"foo"),
        (MessageType.MANAGER_STATUS_REPORT, VALID_CSC_SEGMENT),
        (MessageType.MANAGER_STATUS_REPORT, VALID_CSC_SEGMENT + b"{"),
        (MessageType.EP_STATUS_REPORT, b"foo"),
        (MessageType.EP_STATUS_REPORT, b"foo" * 10),
        (MessageType.EP_STATUS_REPORT, ID_ZERO.bytes + b"{"),
        (MessageType.EP_STATUS_REPORT, b"*" * 100),
        (MessageType.EP_STATUS_REPORT, ID_ZERO.bytes + b"{}"),
        (MessageType.EP_STATUS_REPORT, ID_ZERO.bytes + b"[]"),
        (MessageType.EP_STATUS_REPORT, ID_ZERO.bytes + b"[null,null]"),
        (MessageType.EP_STATUS_REPORT, ID_ZERO.bytes + b"[{},null]"),
        (MessageType.EP_STATUS_REPORT, ID_ZERO.bytes + b"[null,{}]"),
        (MessageType.EP_STATUS_REPORT, ID_ZERO.bytes + b"[{},{},{}]"),
        (MessageType.RESULTS_ACK, b""),
        (MessageType.RESULTS_ACK, b"foo"),
    ],
)
def test_invalid_v0_unpack(message_type, message, v0_packer):
    header = get_v0_header(message_type)
    with pytest.raises(InvalidMessagePayloadError):
        v0_packer.unpack(header + message)
