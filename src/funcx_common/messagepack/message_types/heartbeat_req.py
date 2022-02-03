from __future__ import annotations

from dataclasses import dataclass

from ..common import Message


@dataclass
class HeartbeatReq(Message):
    message_type = "heartbeat_req"
