import typing as t

from ..common import Message, MessageType


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
        b_tid, b_cid, task_buf = buf.decode("utf-8").split(";", 2)
        return cls(b_tid[4:], b_cid[4:], task_buf, raw_buffer=buf)