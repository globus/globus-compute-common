import abc
import enum
import typing as t


class MessageType(enum.Enum):
    HEARTBEAT_REQ = 1
    HEARTBEAT = 2
    EP_STATUS_REPORT = 3
    MANAGER_STATUS_REPORT = 4
    TASK = 5
    RESULTS_ACK = 6


class Message(abc.ABC):
    message_type: t.ClassVar[MessageType]

    @abc.abstractmethod
    def get_v0_body(self) -> bytes:
        """
        Under v0 of the messagepack protocol, each message type must define its own
        payload body.

        This is because the method by which a body is encoded and parsed varies by
        message type.
        """
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def load_v0_body(cls, buf: bytes) -> "Message":
        """
        Under v0 of the messagepack protocol, each message type must define its own
        payload body parsing. The reason is the same as the existence of `get_v0_body`
        """
        raise NotImplementedError()
