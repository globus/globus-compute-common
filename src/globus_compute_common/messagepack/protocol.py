"""
The python protocol definition.

A MessagePackProtocol only needs to define two actions:
  - pack()
  - unpack()

And the two must be inverses on any valid inputs.
"""

import abc

from .message_types import Message


class MessagePackProtocol(abc.ABC):
    @abc.abstractmethod
    def pack(self, message: Message) -> bytes:
        """
        Pack a message into bytes.
        """

    @abc.abstractmethod
    def unpack(self, buf: bytes) -> Message:
        """
        Unpack bytes into a message.
        """
