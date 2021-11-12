import typing as t

from ..common import Message
from .ep_status_report import EPStatusReport
from .heartbeat import Heartbeat
from .heartbeat_req import HeartbeatReq
from .manager_status_report import ManagerStatusReport
from .task import Task

ALL_MESSAGE_TYPES: t.Set[t.Type[Message]] = {
    EPStatusReport,
    Heartbeat,
    HeartbeatReq,
    ManagerStatusReport,
    Task,
}

__all__ = (
    "EPStatusReport",
    "Heartbeat",
    "HeartbeatReq",
    "ManagerStatusReport",
    "Task",
    "ALL_MESSAGE_TYPES",
)
