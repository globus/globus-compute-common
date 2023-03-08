import typing as t
import uuid

from pydantic import Field

from .base import Message, meta
from .task_transition import TaskTransition


@meta(message_type="ep_status_report")
class EPStatusReport(Message):
    """
    Status report for an endpoint, sent from Endpoint to Forwarder.

    Includes EP-wide info such as utilization, as well as per-task status information.
    """

    endpoint_id: uuid.UUID
    global_state: t.Dict[str, t.Any] = Field(alias="ep_status_report")
    task_statuses: t.Dict[str, t.List[TaskTransition]]

    class Config:
        allow_population_by_field_name = True
