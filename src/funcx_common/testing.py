"""
This module defines tools for helping to test funcx_common.
"""
try:
    import redis

    has_redis = True
except ImportError:
    has_redis = False


def _local_redis_reachable() -> bool:  # pragma: no cover
    if has_redis:
        try:
            redis.Redis("localhost", port=6379).ping()
            return True
        except redis.exceptions.ConnectionError:
            pass
    return False


# run this func only once to avoid slowing down the testsuite
LOCAL_REDIS_REACHABLE = _local_redis_reachable()
