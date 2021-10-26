import abc
import typing as t

from ..tasks import TaskProtocol


class TaskStorage(abc.ABC):
    """
    Abstract class which defines the interface for task storage.
    """

    @abc.abstractmethod
    def store_result(self, task: TaskProtocol, result: str) -> bool:
        """
        Store the result of a task.

        If the storage call succeeded, this MUST return True.
        If the storage call failed, an error may be raised or this may return False.
        """

    @abc.abstractmethod
    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        """
        Get the result of a task.

        Returns a string if a result was found, and None otherwise.
        """
