import logging
import uuid

import pytest

from globus_compute_common.redis import (
    ComputeEndpointTaskQueue,
    ComputeRedisPubSub,
    default_redis_connection_factory,
    redis_connection_error_logging,
)
from globus_compute_common.tasks import TaskProtocol, TaskState

try:
    import redis

    has_redis = True
except ImportError:
    has_redis = False


@pytest.mark.skipif(has_redis, reason="test only runs without redis lib")
def test_cannot_create_connection_without_redis_lib():
    with pytest.raises(RuntimeError):
        # can't create a connection
        default_redis_connection_factory()


@pytest.mark.skipif(not has_redis, reason="test requires redis lib")
def test_pubsub_repr():
    pubsub = ComputeRedisPubSub()

    pubsub_str = repr(pubsub)
    assert pubsub_str.startswith("ComputeRedisPubSub")
    assert "host=localhost" in pubsub_str
    assert "port=6379" in pubsub_str

    q_obj = ComputeEndpointTaskQueue("endpoint1")
    assert "endpoint=endpoint1" in repr(q_obj)


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
    task_queue = ComputeEndpointTaskQueue(endpoint)

    # ensure that the error logging wrapper still allows the ConnectionError to
    # propagate
    with pytest.raises(redis.exceptions.ConnectionError):
        task_queue.enqueue(mytask)


@pytest.mark.skipif(not has_redis, reason="test requires redis lib")
def test_connection_error_logging(monkeypatch, caplog):
    def mock_redis_method(*args, **kwargs):
        raise redis.exceptions.ConnectionError("bah humbug!")

    monkeypatch.setattr(redis.Redis, "rpush", mock_redis_method)
    conn = default_redis_connection_factory()

    caplog.set_level(logging.ERROR, logger="globus_compute_common")

    with pytest.raises(redis.exceptions.ConnectionError):
        with redis_connection_error_logging(conn):
            conn.rpush()  # args don't matter...

    assert "ConnectionError while trying to communicate with redis" in caplog.text
