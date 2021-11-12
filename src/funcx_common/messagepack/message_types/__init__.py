import typing as t

from ..common import Message
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
    Task,
    ResultsAck,
}

__all__ = (
    "EPStatusReport",
    "Heartbeat",
    "HeartbeatReq",
    "ManagerStatusReport",
    "Task",
    "ResultsAck",
    "ALL_MESSAGE_CLASSES",
)
