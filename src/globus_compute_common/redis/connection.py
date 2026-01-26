import contextlib
import logging
import os
import typing as t

try:
    import redis

    has_redis = True
except ImportError:
    has_redis = False

log = logging.getLogger(__name__)


def _check_has_redis() -> None:
    # defer this error until the caller tries to instantiate a connection or setup the
    # error log handler, so that imports work even without the 'redis' dependency
    if not has_redis:
        raise RuntimeError("""\
Cannot import globus_compute_common.redis if the 'redis' package is not available.
Either install it explicitly or install the 'redis' extra, as in

    pip install 'globus-compute-common[redis]'

""")


def default_redis_connection_factory(
    redis_url: t.Optional[str] = None,
) -> "redis.Redis[str]":
    """
    Construct a Redis client for a given redis URL.
    If no URL is given, the COMPUTE_COMMON_REDIS_URL environment variable will be used.

    If no URL is given and the environment variable is not populated,

      redis://localhost:6379

    will be used as the default.
    """
    _check_has_redis()

    if redis_url is None:
        redis_url = os.getenv("COMPUTE_COMMON_REDIS_URL", "redis://localhost:6379")

    return redis.Redis.from_url(
        redis_url,
        decode_responses=True,
        health_check_interval=30,
    )


@contextlib.contextmanager
def redis_connection_error_logging(
    redis_client: "redis.Redis[t.Any]",
) -> t.Iterator[None]:
    _check_has_redis()

    try:
        yield
    except redis.exceptions.ConnectionError:
        log.exception(
            "ConnectionError while trying to communicate with redis, %s", redis_client
        )
        raise
