import typing as t

from ..tasks import TaskProtocol
from .base import TaskStorage


class ImplicitRedisStorage(TaskStorage):
    """
    This storage adapter stores task data to redis only.

    It is named "implicit" because it assumes that the task object itself is some form
    of RedisTask which will write to redis either on setattr or some save/commit step.
    """

    def store_result(
        self,
        task: TaskProtocol,
        result: str,
    ) -> None:
        task.result = result
        task.result_reference = {"storage_id": "redis"}

    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        if task.result:
            return task.result
        return None

    def store_payload(
        self,
        task: TaskProtocol,
        payload: str,
    ) -> None:
        task.payload = payload
        task.payload_reference = {"storage_id": "redis"}

    def get_payload(self, task: TaskProtocol) -> t.Optional[str]:
        if task.payload:
            return task.payload
        return None
