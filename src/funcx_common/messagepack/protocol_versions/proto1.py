"""
This file defines Protocol Version 1 of the funcx messagepack protocol.

v1 of the protocol does the following:
- each message is encoded as a JSON object with a two-byte header, with no newlines
- the first byte of the header contains the protocol version, always 1
- the second byte of the header is reserved for future use
- the JSON body contains exactly two fields: "message_type" (a string) and "data" (an object)
- "message_type" determines which class is used to load the content in "data"

For example, under protocol v1, a heartbeat request message could be formulated as

    \x01\x00{"message_type":"heartbeat_req","data":{}}

where `\x01` is the version byte.

A Task message can be formulated with

    \x01\x00{"message_type":"task","data":{"task_id": "359e2ec3-caef-4258-a149-a67767af0ee8","container_id":"ee138b83-fd62-4b57-b31b-55e460569fd2"}}

== Multi-Message Payloads

Because newlines are a forbidden character, multiple messages may be newline-delimited, as in

    \x01\x00{"message_type":"foo","data":{}}
    \x01\x00{"message_type":"bar","data":{}}

== Unknown Field Handling (loading)

The protocol defines the following behavior for missing and unknown fields:
  - if a payload does not contain a required field, loading will fail with
    an InvalidMessagePayloadError
  - if a payload defines fields which are not included in the current message
    definitions, they are silently ignored

Therefore, new fields may be added to the message classes, but they must not be
required until all messages contain those fields.
"""  # noqa: E501
from __future__ import annotations

import dataclasses
import json
import typing as t

from ..common import Message
from ..exceptions import InvalidMessagePayloadError, UnrecognizedMessageTypeError
from ..message_types import ALL_MESSAGE_CLASSES
from ..protocol import MessagePackProtocol

# protocol version and reserved byte as a byte array
_VERSION_BYTE = (1).to_bytes(1, byteorder="big", signed=False)
_RESERVED_BYTE = (0).to_bytes(1, byteorder="big", signed=False)
_STANDARD_HEADER = _VERSION_BYTE + _RESERVED_BYTE


def _field_required(x: dataclasses.Field[t.Any]) -> bool:
    # the following check is misreported by mypy as a non-overlapping check
    # see: https://github.com/python/mypy/issues/12124
    return (
        x.default is dataclasses.MISSING
        and x.default_factory is dataclasses.MISSING  # type: ignore[comparison-overlap]
    )


def _check_required_fields(
    data: dict[str, t.Any], message_class: type[Message]
) -> None:
    required_message_fields = {
        x.name for x in dataclasses.fields(message_class) if _field_required(x)
    }
    data_keys = set(data.keys())
    if not required_message_fields <= data_keys:
        raise InvalidMessagePayloadError(
            f"message body of type {message_class.message_type} was missing required "
            "fields: "
            f"data_keys={data_keys}, required_message_fields={required_message_fields}"
        )


def _filter_data_to_fields(
    data: dict[str, t.Any], message_class: type[Message]
) -> dict[str, t.Any]:
    message_fields = {x.name for x in dataclasses.fields(message_class)}
    return {k: v for k, v in data.items() if k in message_fields}


class MessagePackProtocolV1(MessagePackProtocol):
    MESSAGE_TYPE_MAP: dict[str, type[Message]] = {}

    def pack(self, message: Message) -> bytes:
        body = {
            "message_type": message.message_type,
            "data": message.get_json_safe_dict(),
        }
        # encode() converts to bytes, but no characters will actually be altered because
        # ensure_ascii is being used
        return (
            _STANDARD_HEADER
            + json.dumps(body, separators=(",", ":"), ensure_ascii=True).encode()
        )

    def unpack(self, buf: bytes) -> Message:
        # strip the two byte header
        body = buf[2:]
        envelope = json.loads(body)
        if "message_type" not in envelope:
            raise InvalidMessagePayloadError(
                "cannot unpack message with no message_type"
            )
        if "data" not in envelope:
            raise InvalidMessagePayloadError("cannot unpack message with no data")

        message_type = envelope["message_type"]
        try:
            message_class = self.MESSAGE_TYPE_MAP[message_type]
        except KeyError as e:
            raise UnrecognizedMessageTypeError(f"message_type={message_type}") from e
        data = envelope["data"]
        _check_required_fields(data, message_class)
        return message_class(**_filter_data_to_fields(data, message_class))

    @classmethod
    def register_message_type(cls, message_class: type[Message]) -> None:
        cls.MESSAGE_TYPE_MAP[message_class.message_type] = message_class


for m in ALL_MESSAGE_CLASSES:
    MessagePackProtocolV1.register_message_type(m)
