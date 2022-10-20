import uuid
from datetime import datetime, timedelta

import pytest

try:
    import redis
except ImportError:
    pytest.skip(allow_module_level=True)

from funcx_common.redis_endpoint_lock import RedisEndpointLock
from funcx_common.testing import LOCAL_REDIS_REACHABLE

if not LOCAL_REDIS_REACHABLE:
    pytest.skip(
        "these tests only run with access to local redis", allow_module_level=True
    )


@pytest.fixture(scope="module")
def redis_client():
    with redis.Redis("localhost", port=6379, decode_responses=True) as rc:
        yield rc


@pytest.mark.parametrize("expiration_period_ms", [-1234.5, -4, 0])
def test_redis_lock_invalid_expiration(redis_client, expiration_period_ms):
    endpoint_id = str(uuid.uuid1())
    expiration_time = datetime.now() + timedelta(milliseconds=expiration_period_ms)
    expiration_time_ts = expiration_time.timestamp()
    with pytest.raises(ValueError):
        RedisEndpointLock(
            redis_client,
            endpoint_id,
            lock_timestamp=expiration_time_ts,
        )
