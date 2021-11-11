import typing as t

from .common import Message
from .protocol import MessagePackProtocol
from .protocol_versions.proto0 import MessagePackProtocolV0


class MessagePacker:
    IMPLEMENTATIONS: t.Dict[int, MessagePackProtocol] = {
        0: MessagePackProtocolV0(),
    }

    def __init__(self, default_protocol_version: int = 0) -> None:
        self._default_protocol_version = 0

    # TODO: when new protocol versions are added, replace with protocol detection logic
    def detect_protocol_version(self, buf: bytes) -> int:
        return 0

    def pack(
        self, message: Message, *, protocol_version: t.Optional[int] = None
    ) -> bytes:
        if protocol_version is None:
            protocol_version = self._default_protocol_version
        impl = self.IMPLEMENTATIONS[protocol_version]
        return impl.pack(message)

    def unpack(self, buf: bytes) -> Message:
        protocol_version = self.detect_protocol_version(buf)
        impl = self.IMPLEMENTATIONS[protocol_version]
        return impl.unpack(buf)
