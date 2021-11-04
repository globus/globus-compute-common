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
        self.storages = list(storages)
        self.backward_compatible_storage = None
        for storage in storages:
            if storage.backward_compatible is True:
                self.backward_compatible_storage = storage
                break

    def store_result(self, task: TaskProtocol, result: str) -> bool:
        exception_stack = []
        for store in self.storages:
            try:
                return store.store_result(task, result)
            except StorageException as e:
                exception_stack.append(e)

        raise StorageException(
            f"All storage methods failed to store data: {exception_stack}"
        )

    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        # Return None if result and reference is missing.
        if not task.result and not task.result_reference:
            return None
        # Add backward compatibility with RedisStorage
        # v0.3.3 and prior would only set task.result
        if (
            task.result_reference is None
            and self.backward_compatible_storage is not None
        ):
            return self.backward_compatible_storage.get_result(task)

        # In v0.3.4+ a result_reference is always set when the result is
        # stored. The reference indicated the storage mechanism used.
        if task.result_reference:
            for storage in self.storages:
                t_storage_id = task.result_reference["storage_id"]
                if storage.storage_id == t_storage_id:
                    try:
                        return storage.get_result(task)
                    except StorageException:
                        pass

        raise StorageException("No result stored")
