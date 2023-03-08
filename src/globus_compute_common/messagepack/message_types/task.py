import typing as t
import uuid

from .base import Message, meta
from .container import Container


@meta(message_type="task")
class Task(Message):
    task_id: uuid.UUID

    # for backward compatibility; to be removed when we support only
    # endpoints >= v1.1
    container_id: t.Optional[uuid.UUID]

    container: t.Optional[Container]
    task_buffer: str
