import typing as t

from ..tasks import TaskProtocol
from .base import TaskStorage
from .base import StorageException


class RedisImplicitTaskStorage(TaskStorage):
    """
    RedisImplicitTaskStorage stores values in redis by returning the
    target string in a wrapper so that the storage request is reverse
    delegated to the caller which stores the task.<fields> into REDIS

    This relies on the caller having a mechanism in place to store
    values into redis
    """
    storage_id = 'RedisImplicit'

    def __init__(self) -> None:
        super().__init__()

    def store_result(self, task: TaskProtocol, result: str) -> bool:
        return {self.storage_id: result}

    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        return task.result.get(self.storage_id)


class ThresholdedRedisImplicitTaskStorage(TaskStorage):
    """
    RedisImplicitTaskStorage stores values in redis by returning the
    target string in a wrapper so that the storage request is reverse
    delegated to the caller which stores the task.<fields> into REDIS

    This relies on the caller having a mechanism in place to store
    values into redis
    """
    storage_id = 'ThresholdedRedisImplicit'

    def __init__(self, result_limit_chars: int = 100) -> None:
        super().__init__()
        self.result_limit_chars = result_limit_chars

    def store_result(self, task: TaskProtocol, result: str) -> bool:
        if len(result) <= self.result_limit_chars:
            return {self.storage_id: result}
        else:
            raise StorageException(f"Result size exceeds threshold of {self.result_limit_chars}b")

    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        return task.result.get(self.storage_id)
