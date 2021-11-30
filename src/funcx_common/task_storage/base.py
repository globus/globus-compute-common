import abc
import typing as t

from ..tasks import TaskProtocol


class StorageException(Exception):
    def __init__(self, reason: str):
        self.reason = reason

    def __str__(self) -> str:
        return f"Storage request failed due to reason: {self.reason}"


class TaskStorage(abc.ABC):
    """
    Abstract class which defines the interface for task storage.
    """

    @abc.abstractmethod
    def store_result(self, task: TaskProtocol, result: str) -> None:
        """
        Store the result of a task.
        If the storage call succeeded, set reference to data in Task.result_reference
        If the storage failed, raises StorageException
        """

    @abc.abstractmethod
    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        """
        Get the result of a task.
        Returns a string if a result was found, and None otherwise.
        Raises a storage exception if retrieval failed
        """
