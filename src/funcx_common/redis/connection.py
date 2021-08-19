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
        self.redis_client = redis.Redis(
            host=self.hostname, port=self.port, decode_responses=True
        )

    def _get_str_attrs(self) -> t.List[str]:
        return [f"hostname={self.hostname}", f"port={self.port}"]

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(" + ",".join(self._get_str_attrs()) + ")"

    @staticmethod
    def log_connection_errors(func: t.Callable[..., RT]) -> t.Callable[..., RT]:
        @functools.wraps(func)
        def wrapper(self: FuncxRedisConnection, *args: t.Any, **kwargs: t.Any) -> RT:
            try:
                return func(self, *args, **kwargs)
            except redis.exceptions.ConnectionError:
                log.exception(
                    "ConnectionError while trying to connect to redis@%s:%s",
                    self.hostname,
                    self.port,
                )
                raise

        return wrapper
