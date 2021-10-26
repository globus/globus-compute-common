import typing as t

from ..tasks import TaskProtocol
from .base import TaskStorage


class ChainedTaskStorage(TaskStorage):
    """
    Chained storage combines multiple other concrete storage options.

    The storage methods are used on a "first-come, first-served" basis, with the
    intended usage pattern being

    >>> slow_storage = ...
    >>> fast_storage = ...
    >>> task_storage = ChainedTaskStorage(fast_storage, slow_storage)

    In this scenario, the fast storage will be tried first for both the store and get
    operations.

    The assumption here is that the fast storage responds quickly enough that it can be
    checked first in all cases, even without additional context for the call.
    """

    def __init__(self, *storages: TaskStorage) -> None:
        self._storages = list(storages)

    def store_result(self, task: TaskProtocol, result: str) -> bool:
        for store in self._storages:
            if store.store_result(task, result):
                return True
        return False

    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        for store in self._storages:
            res = store.get_result(task)
            if res is not None:
                return res
        return None
