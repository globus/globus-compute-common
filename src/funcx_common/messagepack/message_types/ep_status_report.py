import typing as t
import uuid

from .base import Message, meta


@meta(message_type="ep_status_report")
class EPStatusReport(Message):
    """
    Status report for an endpoint, sent from Endpoint to Forwarder.

    Includes EP-wide info such as utilization, as well as per-task status information.
    """

    endpoint_id: uuid.UUID
    ep_status_report: t.Dict[str, t.Any]
    task_statuses: t.Dict[str, t.Any]
