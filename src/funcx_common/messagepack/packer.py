from __future__ import annotations

from .exceptions import UnrecognizedProtocolVersion
from .message_types import Message
from .protocol import MessagePackProtocol
from .protocol_versions.proto1 import MessagePackProtocolV1


class MessagePacker:
    IMPLEMENTATIONS: dict[int, MessagePackProtocol] = {
        1: MessagePackProtocolV1(),
    }

    def __init__(self, default_protocol_version: int = 1) -> None:
        self._default_protocol_version = default_protocol_version

    def detect_protocol_version(self, buf: bytes) -> int:
        """read the first byte of the buffer and decode it"""
        if not buf:
            raise ValueError("cannot detect_protocol_version on empty data")
        version_byte = buf[0:1]
        return int.from_bytes(version_byte, byteorder="big", signed=False)

    def pack(self, message: Message, *, protocol_version: int | None = None) -> bytes:
        if protocol_version is None:
            protocol_version = self._default_protocol_version
        impl = self.IMPLEMENTATIONS[protocol_version]
        return impl.pack(message)

    def unpack(self, buf: bytes) -> Message:
        protocol_version = self.detect_protocol_version(buf)
        try:
            impl = self.IMPLEMENTATIONS[protocol_version]
        except KeyError:
            raise UnrecognizedProtocolVersion(
                f"message had unknown protocol version {protocol_version}"
            )
        return impl.unpack(buf)
