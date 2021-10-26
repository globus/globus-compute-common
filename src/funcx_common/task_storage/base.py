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

        If the storage call succeeded, this returns True.
        If the storage call was rejected, this returns False.
        If the call failed, and exception should be raised.

        TaskStorage objects may reject calls without failing. For example, if the
        storage system is a cache of limited size, filling the cache will lead to
        rejected storage.
        """

    @abc.abstractmethod
    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        """
        Get the result of a task.

        Returns a string if a result was found, and None otherwise.
        """


class NullTaskStorage(TaskStorage):
    """
    A TaskStorage which rejects all data and cannot hold data.
    """

    def store_result(self, task: TaskProtocol, result: str) -> bool:
        return False

    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        return None
