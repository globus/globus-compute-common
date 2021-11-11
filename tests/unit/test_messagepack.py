import uuid

import pytest

from funcx_common.messagepack import (
    HeartbeatReq,
    MessagePacker,
    Task,
    UnrecognizedMessageTypeError,
)


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


def test_can_pack_and_unpack_task_v0():
    packer = MessagePacker(default_protocol_version=0)

    task_id = str(uuid.uuid1())
    container_id = str(uuid.uuid1())
    task_obj = Task(task_id, container_id, "some data")

    on_wire = packer.pack(task_obj)
    payload = f"TID={task_id};CID={container_id};some data".encode("utf-8")
    # note, the v0 protocol is sensitive to the message type values
    # "TASK" is 5
    header = b"\x05"
    assert on_wire == header + payload

    task_obj2 = packer.unpack(on_wire)
    assert task_obj2.task_id == task_id
    assert task_obj2.container_id == container_id
    assert task_obj2.task_buffer == "some data"


def test_cannot_unpack_unknown_message_type():
    packer = MessagePacker()

    # as a packed byte, '100'
    header = b"d"
    payload = b"some message"

    with pytest.raises(UnrecognizedMessageTypeError):
        packer.unpack(header + payload)
