import typing as t

from ..tasks import TaskProtocol
from .base import StorageException, TaskStorage


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

    If the fast storage rejects a storage operation, the slow storage will be tried. A
    failure (exception) would be raised immediately, however.

    The assumption here is that the fast storage responds quickly enough that it can be
    checked first in all cases, even without additional context for the call.
    """

    storage_id = "ChainedTaskStorage"

    def __init__(self, *storages: TaskStorage) -> None:
        self._storages = list(storages)
        self.storage_map = {storage.storage_id: storage for storage in storages}

    def store_result(self, task: TaskProtocol, result: str) -> bool:
        exception_stack = []
        for store in self._storages:
            try:
                return store.store_result(task, result)
            except StorageException as e:
                exception_stack.append(e)
                pass

        raise StorageException(
            f"All storage methods failed to store data: {exception_stack}"
        )

    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        # We are special casing here because if the
        if not task.result and not task.result_reference:
            return None
        for store in self._storages:
            if store.storage_id == task.result_reference["storage_id"]:  # type: ignore
                return store.get_result(task)

        return None
