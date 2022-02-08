from __future__ import annotations

import uuid
from dataclasses import dataclass

from ..common import Message


@dataclass
class Heartbeat(Message):
    """
    Generic Heartbeat message, sent in both directions between Forwarder and
    Endpoint.
    """

    message_type = "heartbeat"
    endpoint_id: uuid.UUID
