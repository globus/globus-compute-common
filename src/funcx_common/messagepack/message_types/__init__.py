import typing as t

from .base import Message
from .ep_status_report import EPStatusReport
from .heartbeat import Heartbeat
from .heartbeat_req import HeartbeatReq
from .manager_status_report import ManagerStatusReport
from .results_ack import ResultsAck
from .task import Task

ALL_MESSAGE_CLASSES: t.Set[t.Type[Message]] = {
    EPStatusReport,
    Heartbeat,
    HeartbeatReq,
    ManagerStatusReport,
    ResultsAck,
    Task,
}

__all__ = (
    "Message",
    "EPStatusReport",
    "Heartbeat",
    "HeartbeatReq",
    "ManagerStatusReport",
    "ResultsAck",
    "Task",
    "ALL_MESSAGE_CLASSES",
)
