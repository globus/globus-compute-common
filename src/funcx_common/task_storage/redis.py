import typing as t

from ..tasks import TaskProtocol
from .base import StorageException, TaskStorage


class RedisTaskStorage(TaskStorage):
    """
    RedisImplicitTaskStorage stores values in redis by returning the
    target string in a wrapper so that the storage request is reverse
    delegated to the caller which stores the task.<fields> into REDIS

    This relies on the caller having a mechanism in place to store
    values into redis
    """

    storage_id = "Redis"
    backward_compatible = True

    def __init__(self) -> None:
        super().__init__()

    def store_result(self, task: TaskProtocol, result: str) -> bool:
        task.result = result
        task.result_reference = {"storage_id": self.storage_id}
        return True

    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        if task.result:
            # We raise an exception if the result was stored by
            # a different storage system
            if (
                task.result_reference
                and task.result_reference["storage_id"] != self.storage_id
            ):
                raise StorageException(f"Task not stored with {self.storage_id}")
            else:
                return task.result
        else:
            raise StorageException(f"Task not stored with {self.storage_id}")


class ThresholdedRedisTaskStorage(RedisTaskStorage):
    """
    RedisImplicitTaskStorage stores values in redis by returning the
    target string in a wrapper so that the storage request is reverse
    delegated to the caller which stores the task.<fields> into REDIS

    This relies on the caller having a mechanism in place to store
    values into redis
    """

    storage_id = "ThresholdedRedis"

    def __init__(self, result_limit_chars: int = 100) -> None:
        super().__init__()
        self.result_limit_chars = result_limit_chars

    def store_result(self, task: TaskProtocol, result: str) -> bool:
        if len(result) <= self.result_limit_chars:
            return super().store_result(task, result)
        else:
            raise StorageException(
                f"Result size exceeds threshold of {self.result_limit_chars}b"
            )
