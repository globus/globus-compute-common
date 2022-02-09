import uuid

from .base import Message, meta


@meta(message_type="task")
class Task(Message):
    task_id: uuid.UUID
    container_id: uuid.UUID
    task_buffer: str
