import abc
import typing as t

from ..tasks import TaskProtocol


class StorageException(Exception):
    def __init__(self, reason: str):
        self.reason = reason

    def __str__(self) -> str:
        return f"Storage request failed due to reason:{self.reason}"


class TaskStorage(abc.ABC):
    """
    Abstract class which defines the interface for task storage.
    """

    @abc.abstractmethod
    def store_result(self, task: TaskProtocol, result: str) -> bool:
        """
        Store the result of a task.

        If the storage call succeeded, set reference to data in Task.result_reference
        and return True
        If the call failed, an exception would be raised.
        """

    @property
    @classmethod
    @abc.abstractmethod
    def storage_id(cls) -> str:
        raise NotImplementedError()

    @property
    def backward_compatible(cls) -> bool:
        """
        Indicates backward compatibility with Task from v0.3.3 and older where
        Task.result is used without Task.result_reference
        :return:
        Bool
        """
        return False

    @abc.abstractmethod
    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        """
        Get the result of a task.

        Returns a string if a result was found, and None otherwise.
        Raises a storage exception if retrieval failed
        """


class NullTaskStorage(TaskStorage):
    """
    A TaskStorage which rejects all data and cannot hold data.
    """

    storage_id = "NullTaskStorage"

    def store_result(self, task: TaskProtocol, result: str) -> bool:
        raise StorageException("Null storage does not store")

    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        raise StorageException("Null storage does not store")
