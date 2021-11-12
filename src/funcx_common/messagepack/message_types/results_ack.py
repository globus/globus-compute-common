import uuid

from ..common import Message, MessageType
from ..exceptions import InvalidMessageError


class ResultsAck(Message):
    message_type = MessageType.RESULTS_ACK

    def __init__(self, task_id: str):
        try:
            uuid.UUID(task_id)
        except ValueError as e:
            raise InvalidMessageError(
                "ResultsAck data does not appear to be a UUID"
            ) from e

        self.task_id = task_id

    def get_v0_body(self) -> bytes:
        return self.task_id.encode("ascii")

    @classmethod
    def load_v0_body(cls, buf: bytes) -> "ResultsAck":
        data = buf.decode("ascii")
        return cls(data)
