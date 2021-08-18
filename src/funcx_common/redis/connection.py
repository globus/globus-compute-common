import functools
import logging
import typing as t

try:
    import redis

    has_redis = True
except ImportError:
    has_redis = False

log = logging.getLogger(__name__)

RT = t.TypeVar("RT")


class FuncxRedisConnection:
    """
    A basic redis client wrapper which can be used to inherit and provide a
    working `.redis_client` attribute to child classes.
    """

    def __init__(self, hostname: str, *, port: int = 6379):
        # defer errors over redis being present/absent until someone actually
        # tries to construct a task queue
        # at that point, if redis is not present, error
        # this makes all code in this class which uses `redis` unreachable in
        # that case *except* for method type annotations (for which reason we will
        # quote 'redis' in type annotations to avoid runtime evaluation)
        if not has_redis:
            raise RuntimeError(
                "Cannot construct a FuncxRedisTaskQueue if the 'redis' package "
                "is not available. Either install it explicitly or install the "
                "'redis' extra, as in\n"
                "  pip install 'funcx-common[redis]'"
            )

        self.hostname = hostname
        self.port = port
        self._redis_client: t.Optional[redis.StrictRedis] = None

    def _do_connect(self) -> None:
        try:
            self._redis_client = redis.StrictRedis(
                host=self.hostname, port=self.port, decode_responses=True
            )
            self._redis_client.ping()
        except redis.exceptions.ConnectionError:
            self._redis_client = None
            log.exception(
                "ConnectionError while trying to connect to redis@%s:%s",
                self.hostname,
                self.port,
            )
            raise

    @property
    def is_connected(self) -> bool:
        return self._redis_client is not None

    def ensure_is_connected(self) -> None:
        """imperatively force a connection if one may or may not exist"""
        if not self.is_connected:
            self._do_connect()

    @property
    def redis_client(self) -> "redis.StrictRedis":
        self.ensure_is_connected()
        return t.cast(redis.StrictRedis, self._redis_client)

    def _get_str_attrs(self) -> t.List[str]:
        return [
            f"hostname={self.hostname}",
            f"port={self.port}",
        ]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(" + ",".join(self._get_str_attrs()) + ")"

    @staticmethod
    def method_requires_connection(func: t.Callable[..., RT]) -> t.Callable[..., RT]:
        @functools.wraps(func)
        def wrapper(self: FuncxRedisConnection, *args: t.Any, **kwargs: t.Any) -> RT:
            self.ensure_is_connected()
            return func(self, *args, **kwargs)

        return wrapper
