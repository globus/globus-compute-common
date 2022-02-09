from .base import Message, meta


@meta(message_type="heartbeat_req")
class HeartbeatReq(Message):
    ...
