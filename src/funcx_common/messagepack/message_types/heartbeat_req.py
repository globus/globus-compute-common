from ..common import Message, MessageType


class HeartbeatReq(Message):
    message_type = MessageType.HEARTBEAT_REQ

    def get_v0_body(self) -> bytes:
        return b""

    @classmethod
    def load_v0_body(cls, buf: bytes) -> "HeartbeatReq":
        return cls()
