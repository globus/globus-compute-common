from __future__ import annotations

import typing as t
import uuid

import pydantic

from ...tasks.constants import ActorName, TaskState
from .base import Message, meta


class ResultErrorDetails(pydantic.BaseModel):
    # a string for the error code
    code: str
    # the user is always supposed to see user_message somewhere
    user_message: str


@meta(message_type="result")
class Result(Message):
    task_id: uuid.UUID
    data: str
    error_details: t.Optional[ResultErrorDetails]
    statuses: t.Optional[t.List[t.Tuple[int, TaskState, ActorName]]]

    @property
    def is_error(self) -> bool:
        return self.error_details is not None
