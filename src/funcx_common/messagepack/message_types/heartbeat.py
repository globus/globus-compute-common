import uuid

from .base import Message, meta


@meta(message_type="heartbeat")
class Heartbeat(Message):
    """
    Generic Heartbeat message, sent in both directions between Forwarder and
    Endpoint.
    """

    endpoint_id: uuid.UUID
