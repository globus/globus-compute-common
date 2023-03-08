import uuid

from .base import Message, meta


@meta(message_type="task_cancel")
class TaskCancel(Message):
    task_id: uuid.UUID
