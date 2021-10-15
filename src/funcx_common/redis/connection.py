import contextlib
import logging
import typing as t

try:
    import redis

    has_redis = True
except ImportError:
    has_redis = False

log = logging.getLogger(__name__)
RT = t.TypeVar("RT")

_CONNECTION_FACTORY_T = t.Callable[[str, int], "redis.Redis"]
_OPT_CONNECTION_FACTORY_T = t.Optional[_CONNECTION_FACTORY_T]


def default_redis_connection_factory(hostname: str, port: int) -> "redis.Redis":
    # defer errors over redis being present/absent until someone actually
    # tries to construct a connection
    # this allows general use of `funcx-common` without `redis` installed
    if not has_redis:
        raise RuntimeError(
            "Cannot construct a redis connection if the 'redis' "
            "package is not available. Either install it explicitly or install the "
            "'redis' extra, as in\n"
            "  pip install 'funcx-common[redis]'"
        )

    return redis.Redis(
        host=hostname,
        port=port,
        decode_responses=True,
        health_check_interval=30,
    )


class HasRedisConnection:
    """
    A redis client wrapper which can be used to inherit and provide a
    working `.redis_client` attribute to child classes.
    """

    def __init__(
        self,
        hostname: str,
        *,
        port: int = 6379,
        redis_connection_factory: _OPT_CONNECTION_FACTORY_T = None,
    ) -> None:
        redis_connection_factory = (
            redis_connection_factory or default_redis_connection_factory
        )
        self.redis_client = redis_connection_factory(hostname, port)

    def _get_str_attrs(self) -> t.List[str]:
        return [str(self.redis_client)]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(" + ",".join(self._get_str_attrs()) + ")"

    @contextlib.contextmanager
    def connection_error_logging(self) -> t.Iterator[None]:
        try:
            yield
        except redis.exceptions.ConnectionError:
            log.exception(
                "ConnectionError while trying to communicate with redis, %s", self
            )
            raise
