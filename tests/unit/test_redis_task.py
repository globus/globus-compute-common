import uuid

import pytest

from funcx_common.redis_task import RedisTask
from funcx_common.tasks import InternalTaskState, TaskState
from funcx_common.testing import LOCAL_REDIS_REACHABLE

try:
    import redis

    has_redis = True
except ImportError:
    has_redis = False

if not has_redis or not LOCAL_REDIS_REACHABLE:
    pytest.skip(
        "these tests only run with access to local redis", allow_module_level=True
    )


@pytest.fixture
def redis_client():
    return redis.Redis("localhost", port=6379, decode_responses=True)


@pytest.mark.parametrize(
    "add_kwargs",
    [
        {},
        {"user_id": 10, "function_id": "blah_id"},
        {
            "container": "blahblah_id",
            "payload": "foo bar",
            "payload_reference": {"storage_id": "redis"},
        },
        {"task_group_id": "foo_id"},
    ],
)
def test_redis_task_create(redis_client, add_kwargs):
    task_id = str(uuid.uuid1())
    task = RedisTask(redis_client, task_id, **add_kwargs)

    # required attributes are present and set
    assert hasattr(task, "status")
    assert task.status is not None
    assert task.status == TaskState.WAITING_FOR_EP
    assert hasattr(task, "internal_status")
    assert task.internal_status is not None
    assert task.internal_status == InternalTaskState.INCOMPLETE

    # the TTL is close to the default (could be slightly lower)
    assert (RedisTask.DEFAULT_TTL - task.ttl) < 1

    # other attributes are None if not assigned, and otherwise have the value which was
    # set
    for attrname in [
        "user_id",
        "function_id",
        "container",
        "payload",
        "payload_reference",
        "task_group_id",
    ]:
        assert getattr(task, attrname) == add_kwargs.get(attrname)


def test_redis_task_cannot_increase_ttl(redis_client):
    task_id = str(uuid.uuid1())
    task = RedisTask(redis_client, task_id)

    # attempt to increase the TTL (this will not do anything)
    task.ttl = RedisTask.DEFAULT_TTL * 2
    # the TTL is close to the default (could be slightly lower)
    assert (RedisTask.DEFAULT_TTL - task.ttl) < 1


def test_redis_task_existece_and_deletion(redis_client):
    task_id = str(uuid.uuid1())

    task = RedisTask(redis_client, task_id)  # create
    assert RedisTask.exists(redis_client, task_id)  # exists
    task.delete()  # delete
    assert not RedisTask.exists(redis_client, task_id)  # does not exist


def test_redis_task_load(redis_client):
    task_id = str(uuid.uuid1())

    # no such task
    with pytest.raises(ValueError):
        RedisTask.load(redis_client, task_id)

    RedisTask(redis_client, task_id)  # create

    # load works
    task = RedisTask.load(redis_client, task_id)
    assert isinstance(task, RedisTask)
