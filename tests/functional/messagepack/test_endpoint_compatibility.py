import uuid

import pytest

from funcx_common.messagepack import MessagePacker
from funcx_common.messagepack.message_types import (
    EPStatusReport,
    Heartbeat,
    HeartbeatReq,
    ManagerStatusReport,
    ResultsAck,
    Task,
)

try:
    from funcx_endpoint.executors.high_throughput import messages as EP
except ImportError:
    pytest.skip(
        "these tests require availability of the funcx_endpoint package",
        allow_module_level=True,
    )


@pytest.fixture
def v0_packer():
    return MessagePacker(default_protocol_version=0)


def test_ep_status_report(v0_packer):
    endpoint_id = str(uuid.uuid1())
    orig = EPStatusReport(endpoint_id, {"foo": "bar"}, {"foo": "baz"})
    on_wire = v0_packer.pack(orig)

    ep_report = EP.Message.unpack(on_wire)
    assert isinstance(ep_report, EP.EPStatusReport)
    # there is no `endpoint_id`, just the bytes of the ID in a field named `_header`
    # this assert is "what we mean":
    #   assert ep_report.endpoint_id == endpoint_id
    assert str(uuid.UUID(bytes=ep_report._header)) == endpoint_id
    assert ep_report.ep_status == {"foo": "bar"}
    assert ep_report.task_statuses == {"foo": "baz"}

    on_wire2 = ep_report.pack()
    common_report = v0_packer.unpack(on_wire2)
    assert isinstance(common_report, EPStatusReport)
    assert common_report.endpoint_id == endpoint_id
    assert common_report.ep_status == {"foo": "bar"}
    assert common_report.task_statuses == {"foo": "baz"}


def test_heartbeat(v0_packer):
    endpoint_id = str(uuid.uuid1())
    orig = Heartbeat(endpoint_id)
    on_wire = v0_packer.pack(orig)

    ep_hb = EP.Message.unpack(on_wire)
    assert isinstance(ep_hb, EP.Heartbeat)
    assert ep_hb.endpoint_id == endpoint_id

    on_wire2 = ep_hb.pack()
    common_hb = v0_packer.unpack(on_wire2)
    assert isinstance(common_hb, Heartbeat)
    assert common_hb.endpoint_id == endpoint_id


def test_heartbeat_req(v0_packer):
    orig = HeartbeatReq()
    on_wire = v0_packer.pack(orig)

    ep_hbr = EP.Message.unpack(on_wire)
    assert isinstance(ep_hbr, EP.HeartbeatReq)

    on_wire2 = ep_hbr.pack()
    common_hbr = v0_packer.unpack(on_wire2)
    assert isinstance(common_hbr, HeartbeatReq)


def test_manager_status_report(v0_packer):
    orig = ManagerStatusReport({"foo": "bar"}, 105)
    on_wire = v0_packer.pack(orig)

    ep_report = EP.Message.unpack(on_wire)
    assert isinstance(ep_report, EP.ManagerStatusReport)
    assert ep_report.task_statuses == {"foo": "bar"}
    assert ep_report.container_switch_count == 105

    on_wire2 = ep_report.pack()
    common_report = v0_packer.unpack(on_wire2)
    assert isinstance(common_report, ManagerStatusReport)
    assert common_report.task_statuses == {"foo": "bar"}
    assert common_report.container_switch_count == 105


def test_results_ack(v0_packer):
    task_id = str(uuid.uuid1())
    orig = ResultsAck(task_id)
    on_wire = v0_packer.pack(orig)

    ep_ack = EP.Message.unpack(on_wire)
    assert isinstance(ep_ack, EP.ResultsAck)
    assert ep_ack.task_id == task_id

    on_wire2 = ep_ack.pack()
    common_ack = v0_packer.unpack(on_wire2)
    assert isinstance(common_ack, ResultsAck)
    assert common_ack.task_id == task_id


def test_task(v0_packer):
    task_id = str(uuid.uuid1())
    container_id = str(uuid.uuid1())
    orig = Task(task_id, container_id, "some data")
    on_wire = v0_packer.pack(orig)

    ep_task = EP.Message.unpack(on_wire)
    assert isinstance(ep_task, EP.Task)
    assert ep_task.task_id == task_id
    assert ep_task.container_id == container_id
    # NOTE: this is a known difference between the implementations, that
    # `funcx-endpoint` implements this as storing bytes when loaded, but
    # `funcx-common` will store as a string instead
    assert ep_task.task_buffer == b"some data"

    on_wire2 = ep_task.pack()
    common_task = v0_packer.unpack(on_wire2)
    assert isinstance(common_task, Task)
    assert common_task.task_id == task_id
    assert common_task.container_id == container_id
    assert common_task.task_buffer == "some data"
