import uuid

import pytest

from funcx_common.redis import FuncxEndpointTaskQueue, FuncxRedisConnection
from funcx_common.tasks import TaskProtocol, TaskState

try:
    import redis

    has_redis = True
except ImportError:
    has_redis = False


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
