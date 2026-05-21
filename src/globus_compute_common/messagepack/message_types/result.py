from __future__ import annotations

import typing as t
import uuid

import pydantic

from .base import Message, meta
from .task_transition import TaskTransition


class ResultErrorDetails(pydantic.BaseModel):
    # a string for the error code
    code: str
    # the user is always supposed to see user_message somewhere
    user_message: str


@meta(message_type="result")
class Result(Message):
    task_id: uuid.UUID
    data: str
    details: t.Optional[t.Dict[t.Any, t.Any]] = None
    error_details: t.Optional[ResultErrorDetails] = None
    task_statuses: t.Optional[t.List[TaskTransition]] = None

    @property
    def is_error(self) -> bool:
        return self.error_details is not None
