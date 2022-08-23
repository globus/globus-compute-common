import typing as t

from .base import Message
from .ep_status_report import EPStatusReport
from .manager_status_report import ManagerStatusReport
from .result import Result, ResultErrorDetails
from .task import Task
from .task_cancel import TaskCancel
from .task_transition import TaskTransition

ALL_MESSAGE_CLASSES: t.Set[t.Type[Message]] = {
    EPStatusReport,
    ManagerStatusReport,
    Task,
    TaskCancel,
    Result,
    TaskTransition,
}

__all__ = (
    "Message",
    "EPStatusReport",
    "ManagerStatusReport",
    "Task",
    "TaskCancel",
    "Result",
    "ResultErrorDetails",
    "TaskTransition",
    "ALL_MESSAGE_CLASSES",
)
