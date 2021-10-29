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
    def store_result(self, task: TaskProtocol, result: str) -> dict[str, str]:
        """
        Store the result of a task.

        If the storage call succeeded, return a reference (dict) to the data
        If the call failed, an exception would be raised.
        """

    @property
    @classmethod
    @abc.abstractmethod
    def storage_id(cls):
        return NotImplementedError

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
    storage_id = 'NullTaskStorage'

    def store_result(self, task: TaskProtocol, result: str) -> bool:
        raise StorageException("Null storage does not store")

    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        raise StorageException("Null storage does not store")
