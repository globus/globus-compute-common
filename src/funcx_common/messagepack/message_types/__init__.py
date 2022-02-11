import typing as t

from .base import Message
from .ep_status_report import EPStatusReport
from .manager_status_report import ManagerStatusReport
from .result import Result, ResultErrorDetails
from .task import Task
from .task_cancel import TaskCancel

ALL_MESSAGE_CLASSES: t.Set[t.Type[Message]] = {
    EPStatusReport,
    ManagerStatusReport,
    Task,
    TaskCancel,
    Result,
}

__all__ = (
    "Message",
    "EPStatusReport",
    "ManagerStatusReport",
    "Task",
    "TaskCancel",
    "Result",
    "ResultErrorDetails",
    "ALL_MESSAGE_CLASSES",
)
