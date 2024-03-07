import typing as t
import uuid

import pydantic
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
        version = [int(num) for num in pydantic.__version__.split(".")]
        major_version = version[0]
        if major_version == 2:
            # In Pydantic V2, `allow_population_by_field_name` was renamed to
            # `populate_by_name`, see:
            # https://docs.pydantic.dev/latest/migration/#changes-to-config
            populate_by_name = True
        else:
            allow_population_by_field_name = True
