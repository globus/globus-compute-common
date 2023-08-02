import random
import uuid

import pytest

from globus_compute_common.redis_task import RedisTask
from globus_compute_common.tasks import InternalTaskState, TaskState
from globus_compute_common.testing import LOCAL_REDIS_REACHABLE

try:
    import redis

    has_redis = True
except ImportError:
    has_redis = False

if not has_redis or not LOCAL_REDIS_REACHABLE:
    pytest.skip(
        "these tests only run with access to local redis", allow_module_level=True
    )


@pytest.fixture(autouse=True)
def lower_ttl_for_test():
    RedisTask.DEFAULT_TTL = 10  # Play nice with local infrastructure


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
        {"queue_name": "foo_name"},
        {
            "payload": "abc",
            "details": {
                "Blah_Version": "3.10.4",
                "Blah number": 1234,
            },
        },
        {
            "payload": "something",
        },
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
        "queue_name",
    ]:
        assert getattr(task, attrname) == add_kwargs.get(attrname)

    if "details" in add_kwargs:
        for k, v in add_kwargs["details"].items():
            assert task.details[k] == v
    else:
        assert task.details is None


def test_redis_task_cannot_increase_ttl(redis_client):
    task_id = str(uuid.uuid1())
    task = RedisTask(redis_client, task_id)

    # attempt to increase the TTL (this will not do anything)
    task.ttl = RedisTask.DEFAULT_TTL * 2
    # the TTL is close to the default (could be slightly lower)
    assert (RedisTask.DEFAULT_TTL - task.ttl) < 1


def test_redis_task_existence_and_deletion(redis_client):
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


def test_redis_state_log(redis_client):
    task_id = str(uuid.uuid4())

    rt = RedisTask(redis_client, task_id)
    to_store = [f"some message: {i}" for i in range(random.randrange(1, 10))]
    for msg in to_store:
        rt.status_log = msg

    assert to_store == rt.status_log
    assert 0 < redis_client.ttl(rt.state_log_name) <= rt.DEFAULT_TTL
