import queue
import typing as t

from ..tasks import TaskProtocol, TaskState
from .connection import default_redis_connection_factory

if t.TYPE_CHECKING:
    import redis


class FuncxEndpointTaskQueue:
    def __init__(
        self, endpoint: str, *, redis_client: t.Optional["redis.Redis[t.Any]"] = None
    ) -> None:
        if redis_client is None:
            redis_client = default_redis_connection_factory()
        self.redis_client = redis_client
        self.endpoint = endpoint

    def __repr__(self) -> str:
        attr_str = f"endpoint={self.endpoint},redis_client={self.redis_client}"
        return f"FuncxEndpointTaskQueue({attr_str})"

    @property
    def queue_name(self) -> str:
        return f"task_{self.endpoint}_list"

    def enqueue(self, task: TaskProtocol) -> None:
        task.endpoint = self.endpoint
        task.status = TaskState.WAITING_FOR_EP
        self.redis_client.rpush(self.queue_name, task.task_id)

    def dequeue(self, *, timeout: int = 1) -> str:
        res = self.redis_client.blpop(self.queue_name, timeout=timeout)
        if not res:
            raise queue.Empty
        _queue_name, task_id = res
        return t.cast(str, task_id)
