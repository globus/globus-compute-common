import typing as t
import uuid

from ..common import Message, MessageType
from ..exceptions import InvalidMessagePayloadError


class Task(Message):
    message_type = MessageType.TASK

    def __init__(
        self,
        task_id: str,
        container_id: str,
        task_buffer: str,
        raw_buffer: t.Optional[bytes] = None,
    ):
        self.task_id = task_id
        self.container_id = container_id
        self.task_buffer = task_buffer
        self.raw_buffer = raw_buffer

    def get_v0_body(self) -> bytes:
        if self.raw_buffer is None:
            self.raw_buffer = (
                f"TID={self.task_id};CID={self.container_id};{self.task_buffer}".encode(
                    "utf-8"
                )
            )
        return self.raw_buffer

    @classmethod
    def load_v0_body(cls, buf: bytes) -> "Task":
        data = buf.decode("utf-8")
        if data.count(";") < 2:
            raise InvalidMessagePayloadError(
                "Task body did not contain enough ';' delimiters"
            )
        tid, cid, task_buf = buf.decode("utf-8").split(";", 2)

        if len(tid) < 4 or len(cid) < 4:
            raise InvalidMessagePayloadError("Task body TID or CID appear invalid")

        # trim "TID=" and "CID=" from the front
        tid = tid[4:]
        cid = cid[4:]

        try:
            uuid.UUID(tid)
        except ValueError as e:
            raise InvalidMessagePayloadError(
                "Task data contains TID which does not appear to be a UUID"
            ) from e

        try:
            uuid.UUID(cid)
        except ValueError as e:
            raise InvalidMessagePayloadError(
                "Task data contains CID which does not appear to be a UUID"
            ) from e
        return cls(tid, cid, task_buf, raw_buffer=buf)
