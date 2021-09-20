import queue
import uuid

import pytest

from funcx_common.redis import FuncxEndpointTaskQueue
from funcx_common.tasks import TaskProtocol, TaskState
from funcx_common.testing import LOCAL_REDIS_REACHABLE


@pytest.mark.skipif(
    not LOCAL_REDIS_REACHABLE, reason="test requires local redis reachable"
)
def test_enqueue_and_dequeue_simple_task():
    class SimpleInMemoryTask(TaskProtocol):
        def __init__(self):
            self.task_id = str(uuid.uuid1())
            self.endpoint = None
            self.status = TaskState.RECEIVED

    mytask = SimpleInMemoryTask()
    endpoint = str(uuid.uuid1())
    task_queue = FuncxEndpointTaskQueue("localhost", endpoint)

    assert mytask.endpoint is None

    task_queue.enqueue(mytask)

    assert mytask.endpoint == endpoint
    assert mytask.status is TaskState.WAITING_FOR_EP

    dequeued_task_id = task_queue.dequeue()

    assert dequeued_task_id == mytask.task_id


@pytest.mark.skipif(
    not LOCAL_REDIS_REACHABLE, reason="test requires local redis reachable"
)
def test_dequeue_empty_behavior():
    endpoint = str(uuid.uuid1())
    task_queue = FuncxEndpointTaskQueue("localhost", endpoint)

    with pytest.raises(queue.Empty):
        task_queue.dequeue()
