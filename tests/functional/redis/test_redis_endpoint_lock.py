import uuid
from datetime import datetime, timedelta
from time import sleep

import pytest

try:
    import redis
except ImportError:
    pytest.skip(allow_module_level=True)

from globus_compute_common.redis_endpoint_lock import RedisEndpointLock
from globus_compute_common.testing import LOCAL_REDIS_REACHABLE

if not LOCAL_REDIS_REACHABLE:
    pytest.skip(
        "these tests only run with access to local redis", allow_module_level=True
    )


@pytest.fixture(scope="module")
def redis_client():
    with redis.Redis("localhost", port=6379, decode_responses=True) as rc:
        yield rc


@pytest.fixture
def future_ts():
    future_time = datetime.now() + timedelta(seconds=30)
    return future_time.timestamp()


def test_redis_lock_load_non_existing(redis_client):
    with pytest.raises(ValueError, match="Cannot find lock"):
        RedisEndpointLock.load(redis_client, str(uuid.uuid1()))


@pytest.mark.parametrize("ttl_ms", [456.4, 1100.0])
def test_redis_lock_create_expire(redis_client, ttl_ms):
    endpoint_id = str(uuid.uuid1())
    expiration_time = datetime.now() + timedelta(milliseconds=ttl_ms)
    expiration_time_ts = expiration_time.timestamp()

    assert not RedisEndpointLock.exists(redis_client, endpoint_id)

    lock = RedisEndpointLock(
        redis_client,
        endpoint_id,
        lock_timestamp=expiration_time_ts,
    )

    assert hasattr(lock, "hname")
    assert lock.hname.startswith("endpoint_lock_")
    assert hasattr(lock, "expire_ts")

    assert RedisEndpointLock.exists(redis_client, endpoint_id)

    loaded_lock = RedisEndpointLock.load(redis_client, endpoint_id)
    assert loaded_lock.lock_expiration_ts == expiration_time_ts

    # Test waiting times @parametrize can't be too high or wait is long
    sleep(ttl_ms / 1000)
    assert not RedisEndpointLock.exists(redis_client, endpoint_id)


def test_redis_lock_existence_and_deletion(redis_client, future_ts):
    endpoint_id = str(uuid.uuid1())

    lock = RedisEndpointLock(
        redis_client, endpoint_id, lock_timestamp=future_ts
    )  # create
    assert RedisEndpointLock.exists(redis_client, endpoint_id)  # exists
    lock.delete()  # delete
    assert not RedisEndpointLock.exists(redis_client, endpoint_id)
