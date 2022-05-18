from __future__ import annotations

import typing as t
import uuid

import pydantic

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
    exec_start_ms: t.Optional[int]
    exec_end_ms: t.Optional[int]
    # storage for the computed property, "private" (meaning it will not appear in
    # serialized data)
    _exec_duration_ms: t.Optional[int] = None

    @property
    def is_error(self) -> bool:
        return self.error_details is not None

    @property
    def exec_duration_ms(self) -> t.Optional[int]:
        if self._exec_duration_ms is None:
            if self.exec_start_ms is None or self.exec_end_ms is None:
                return None
            self._exec_duration_ms = self.exec_end_ms - self.exec_start_ms
        return self._exec_duration_ms
