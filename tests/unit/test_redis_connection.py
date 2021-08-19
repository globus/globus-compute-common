import queue
import uuid

import pytest

from funcx_common.redis import FuncxEndpointTaskQueue, FuncxRedisConnection
from funcx_common.tasks import TaskProtocol, TaskState

try:
    import redis

    has_redis = True
except ImportError:
    has_redis = False


def _local_redis_reachable():
    # run this func only once to avoid slowing down the testsuite
    if not hasattr(_local_redis_reachable, "_result"):
        _local_redis_reachable._result = None
    if _local_redis_reachable._result is None:
        _local_redis_reachable._result = False
        if has_redis:
            try:
                redis.Redis("localhost", port=6379).ping()
                _local_redis_reachable._result = True
            except redis.exceptions.ConnectionError:
                pass
    return _local_redis_reachable._result


@pytest.mark.skipif(has_redis, reason="test only runs without redis lib")
def test_cannot_create_connection_without_redis_lib():
    with pytest.raises(RuntimeError):
        # can't create a connection
        FuncxRedisConnection("localhost")


@pytest.mark.skipif(not has_redis, reason="test requires redis lib")
def test_str_form(monkeypatch):
    conn_obj = FuncxRedisConnection("localhost")
    stred = str(conn_obj)
    assert stred.startswith("FuncxRedisConnection(")
    assert "hostname=localhost" in stred
    assert "port=6379" in stred

    q_obj = FuncxEndpointTaskQueue("localhost", "endpoint1")
    assert "endpoint=endpoint1" in str(q_obj)


@pytest.mark.skipif(
    not _local_redis_reachable(), reason="test requires local redis reachable"
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
    not _local_redis_reachable(), reason="test requires local redis reachable"
)
def test_dequeue_empty_behavior():
    endpoint = str(uuid.uuid1())
    task_queue = FuncxEndpointTaskQueue("localhost", endpoint)

    with pytest.raises(queue.Empty):
        task_queue.dequeue()


@pytest.mark.skipif(not has_redis, reason="test requires redis lib")
def test_connection_error_on_enqueue(monkeypatch):
    class SimpleInMemoryTask(TaskProtocol):
        def __init__(self):
            self.task_id = str(uuid.uuid1())
            self.endpoint = None
            self.status = TaskState.RECEIVED

    def mock_redis_method(*args, **kwargs):
        raise redis.exceptions.ConnectionError("bah humbug!")

    monkeypatch.setattr(redis.Redis, "rpush", mock_redis_method)

    mytask = SimpleInMemoryTask()
    endpoint = str(uuid.uuid1())
    task_queue = FuncxEndpointTaskQueue("localhost", endpoint)

    # ensure that the error logging wrapper still allows the ConnectionError to
    # propagate
    with pytest.raises(redis.exceptions.ConnectionError):
        task_queue.enqueue(mytask)
