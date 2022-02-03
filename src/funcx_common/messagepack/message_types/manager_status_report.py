from __future__ import annotations

import typing as t
from dataclasses import dataclass

from ..common import Message


@dataclass
class ManagerStatusReport(Message):
    """
    Status report sent from the Manager to the Endpoint, which mostly just amounts to
    saying which tasks are now RUNNING.
    """

    message_type = "manager_status_report"
    task_statuses: dict[str, t.Any]
