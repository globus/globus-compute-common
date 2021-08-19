import queue
import typing as t

from ..tasks import TaskProtocol, TaskState
from .connection import FuncxRedisConnection


class FuncxEndpointTaskQueue(FuncxRedisConnection):
    def __init__(self, hostname: str, endpoint: str, *, port: int = 6379):
        self.endpoint = endpoint
        super().__init__(hostname, port=port)

    def _get_str_attrs(self) -> t.List[str]:
        return [f"endpoint={self.endpoint}"] + super()._get_str_attrs()

    @property
    def queue_name(self) -> str:
        return f"task_{self.endpoint}_list"

    @FuncxRedisConnection.log_connection_errors
    def enqueue(self, task: TaskProtocol) -> None:
        task.endpoint = self.endpoint
        task.status = TaskState.WAITING_FOR_EP
        self.redis_client.rpush(self.queue_name, task.task_id)

    @FuncxRedisConnection.log_connection_errors
    def dequeue(self, *, timeout: int = 1) -> str:
        res = self.redis_client.blpop(self.queue_name, timeout=timeout)
        if not res:
            raise queue.Empty
        _queue_name, task_id = res
        return task_id
