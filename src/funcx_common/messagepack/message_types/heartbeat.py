import uuid

from ..common import Message, MessageType
from ..exceptions import InvalidMessageError


class Heartbeat(Message):
    """
    Generic Heartbeat message, sent in both directions between Forwarder and
    Endpoint.
    """

    message_type = MessageType.HEARTBEAT

    def __init__(self, endpoint_id: str) -> None:
        try:
            uuid.UUID(endpoint_id)
        except ValueError as e:
            raise InvalidMessageError(
                "Heartbeat data does not appear to be a UUID"
            ) from e
        self.endpoint_id: str = endpoint_id

    def get_v0_body(self) -> bytes:
        return self.endpoint_id.encode("ascii")

    @classmethod
    def load_v0_body(cls, buf: bytes) -> "Heartbeat":
        data = buf.decode("ascii")
        return cls(data)
