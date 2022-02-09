import uuid

from .base import Message, meta


@meta(message_type="results_ack")
class ResultsAck(Message):
    task_id: uuid.UUID
