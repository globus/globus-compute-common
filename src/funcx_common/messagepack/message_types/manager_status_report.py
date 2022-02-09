import typing as t

from .base import Message, meta


@meta(message_type="manager_status_report")
class ManagerStatusReport(Message):
    """
    Status report sent from the Manager to the Endpoint, which mostly just amounts to
    saying which tasks are now RUNNING.
    """

    task_statuses: t.Dict[str, t.Any]
