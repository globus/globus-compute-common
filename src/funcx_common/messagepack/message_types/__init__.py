import typing as t

from .base import Message
from .container import Container, ContainerImage
from .ep_status_report import EPStatusReport
from .manager_status_report import ManagerStatusReport
from .result import Result, ResultErrorDetails
from .task import Task
from .task_cancel import TaskCancel
from .task_transition import TaskTransition

ALL_MESSAGE_CLASSES: t.Set[t.Type[Message]] = {
    Container,
    ContainerImage,
    EPStatusReport,
    ManagerStatusReport,
    Task,
    TaskCancel,
    Result,
    TaskTransition,
}

__all__ = (
    "Message",
    "Container",
    "ContainerImage",
    "EPStatusReport",
    "ManagerStatusReport",
    "Task",
    "TaskCancel",
    "Result",
    "ResultErrorDetails",
    "TaskTransition",
    "ALL_MESSAGE_CLASSES",
)
