"""
This file defines Protocol Version 0 of the funcx messagepack protocol.

v0 of the protocol does the following:
- messages are encoded as packed bytes with the python `struct` library
- the first byte is always the message type
- messages may be packed as strings with inner delimiters

For example, under protocol v0, a heartbeat request message can be formulated with

    >>> packer = struct.Struct('b')
    >>> packer.pack(1)

where `1` is the indicator for heartbeat requests.

A Task message can be formulated with

    >>> packer = struct.Struct('b')
    >>> msg = packer.pack(5)  # 5 is for Tasks
    >>> msg += f"TID={task_id};CID={container_id};{task_buffer}".encode("utf-8")

Note that this means that message unpacking in v0 may require additional parsing. In the
case of tasks, `message.split(";", 2)` is needed.
"""
import typing as t
from struct import Struct

from ..common import Message, MessageType
from ..exceptions import UnrecognizedMessageTypeError
from ..message_types import ALL_MESSAGE_CLASSES
from ..protocol import MessagePackProtocol

_MESSAGE_TYPE_FORMATTER = Struct("b")


class MessagePackProtocolV0(MessagePackProtocol):
    MESSAGE_TYPE_MAP: t.Dict[MessageType, t.Type[Message]] = {}

    def pack(self, message: Message) -> bytes:
        prefix = _MESSAGE_TYPE_FORMATTER.pack(message.message_type.value)
        body = message.get_v0_body()
        return prefix + body

    def unpack(self, buf: bytes) -> Message:
        (message_type,) = _MESSAGE_TYPE_FORMATTER.unpack_from(buf, offset=0)
        remainder = buf[_MESSAGE_TYPE_FORMATTER.size :]
        try:
            mtype = MessageType(message_type)
        except ValueError as e:
            raise UnrecognizedMessageTypeError(f"message_type={message_type}") from e

        message_class = self.MESSAGE_TYPE_MAP[mtype]
        return message_class.load_v0_body(remainder)

    @classmethod
    def register_message_type(cls, message_class: t.Type[Message]) -> None:
        cls.MESSAGE_TYPE_MAP[message_class.message_type] = message_class


for m in ALL_MESSAGE_CLASSES:
    MessagePackProtocolV0.register_message_type(m)
