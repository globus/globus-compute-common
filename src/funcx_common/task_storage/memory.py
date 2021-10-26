import typing as t

from ..tasks import TaskProtocol
from .base import TaskStorage


class MemoryTaskStorage(TaskStorage):
    """
    The simplest possible task storage system: an in-memory dictionary.

    This is meant to
    - demonstrate a complete implementation of the TaskStorage interface
    - be usable in testsuites or other contexts which want an in-process storage system
    """

    def __init__(self) -> None:
        self._results: t.Dict[str, str] = {}

    def store_result(self, task: TaskProtocol, result: str) -> bool:
        self._results[task.task_id] = result
        return True

    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        return self._results.get(task.task_id)


class ThresholdedMemoryTaskStorage(MemoryTaskStorage):
    """
    ThresholdedMemoryTaskStorage must be constructed with a size limit.
    If the length of a result exceeds the limit, it will be rejected from the store
    operation.

    Otherwise, it is the same as MemoryTaskStorage.

    Note that the result limit is given in number of characters, not bytes. TaskStorage
    handles strings, and we don't want to do any extra encode/decode passes.
    """

    def __init__(self, result_limit_chars: int = 100) -> None:
        self._result_limit_chars = result_limit_chars
        super().__init__()

    def store_result(self, task: TaskProtocol, result: str) -> bool:
        if len(result) > self._result_limit_chars:
            return False

        self._results[task.task_id] = result
        return True
