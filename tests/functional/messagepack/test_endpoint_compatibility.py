import uuid

import pytest

from funcx_common.messagepack import MessagePacker
from funcx_common.messagepack.message_types import Task

try:
    from funcx_endpoint.executors.high_throughput.messages import Message as EP_Message
    from funcx_endpoint.executors.high_throughput.messages import Task as EP_Task
except ImportError:
    pytest.skip(
        "these tests require availability of the funcx_endpoint package",
        allow_module_level=True,
    )


@pytest.fixture
def v0_packer():
    return MessagePacker(default_protocol_version=0)


def test_task_compatibility(v0_packer):
    task_id = str(uuid.uuid1())
    container_id = str(uuid.uuid1())
    orig_task = Task(task_id, container_id, "some data")

    on_wire = v0_packer.pack(orig_task)

    ep_task = EP_Message.unpack(on_wire)
    assert isinstance(ep_task, EP_Task)
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
