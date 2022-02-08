"""
This file defines Protocol Version 1 of the funcx messagepack protocol.

v1 of the protocol does the following:
- each message is encoded as a JSON object in UTF-8 with a one-byte header, no newlines
- the first byte of the header contains the protocol version, always 1
- the JSON body contains exactly two fields: "message_type" (a string) and "data" (an object)
- "message_type" determines which class is used to load the content in "data"

For example, under protocol v1, a heartbeat request message could be formulated as

    \x01{"message_type":"heartbeat_req","data":{}}

where `\x01` is the version byte.

A Task message can be formulated with

    \x01{"message_type":"task","data":{"task_id": "359e2ec3-caef-4258-a149-a67767af0ee8","container_id":"ee138b83-fd62-4b57-b31b-55e460569fd2"}}

== Multi-Message Payloads

Because newlines are a forbidden character, multiple messages may be newline-delimited, as in

    \x01{"message_type":"foo","data":{}}
    \x01{"message_type":"bar","data":{}}

== Unknown Field Handling (loading)

The protocol defines the following behavior for missing and unknown fields:

  - if a payload does not contain a required field, loading will fail with an
    InvalidMessagePayloadError

  - if a payload defines fields which are not included in the current message
    definitions, they are ignored and a warning is logged

  - if an envelope includes unknown fields (other than "message_type" and "data"), they
    are ignored and a warning is logged

Therefore, new fields may be added to the message classes, but they must not be
required until all messages contain those fields.
"""  # noqa: E501
from __future__ import annotations

import dataclasses
import json
import logging
import typing as t
import uuid

from ..common import Message, is_uuid_field
from ..exceptions import InvalidMessagePayloadError, UnrecognizedMessageTypeError
from ..message_types import ALL_MESSAGE_CLASSES
from ..protocol import MessagePackProtocol

log = logging.getLogger(__name__)

# protocol version and reserved byte as a byte array
_VERSION_BYTE = (1).to_bytes(1, byteorder="big", signed=False)


def _typename(x: t.Any) -> str:
    return type(x).__name__


def _convert_json_unsafe(data: t.Any) -> t.Any:
    if isinstance(data, dict):
        return {k: _convert_json_unsafe(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_convert_json_unsafe(x) for x in data]
    elif isinstance(data, uuid.UUID):
        return str(data)
    else:
        return data


def _json_safe_dict(msg: Message) -> dict[str, t.Any]:
    return t.cast(t.Dict[str, t.Any], _convert_json_unsafe(dataclasses.asdict(msg)))


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
    missing_fields = {x for x in required_message_fields if x not in data}
    if missing_fields:
        raise InvalidMessagePayloadError(
            f"message body of type {message_class.message_type} was missing required "
            f"fields: {missing_fields}"
        )


def _filter_data_to_fields(
    data: dict[str, t.Any], message_class: type[Message]
) -> dict[str, t.Any]:
    message_fields = {x.name for x in dataclasses.fields(message_class)}
    filtered_fields = {k: v for k, v in data.items() if k in message_fields}
    unknown_fields = {x for x in data if x not in message_fields}
    if unknown_fields:
        log.warning(
            "encountered unknown data fields while reading a %s message: %s",
            message_class.message_type,
            unknown_fields,
        )
    return filtered_fields


def _convert_fields(
    data: dict[str, t.Any], message_class: type[Message]
) -> dict[str, t.Any]:
    message_fields = {x.name: x for x in dataclasses.fields(message_class)}

    def convert_field(name: str, value: t.Any) -> t.Any:
        field_obj = message_fields[name]
        if is_uuid_field(field_obj):
            try:
                return uuid.UUID(value)
            except ValueError as e:
                raise InvalidMessagePayloadError(f"invalid UUID: {value}") from e
        return value

    return {k: convert_field(k, v) for k, v in data.items()}


def _load_from_json(data: dict[str, t.Any], message_class: type[Message]) -> Message:
    _check_required_fields(data, message_class)
    data = _filter_data_to_fields(data, message_class)
    data = _convert_fields(data, message_class)
    return message_class(**data)


def _check_envelope(envelope: t.Any) -> None:
    if not isinstance(envelope, dict):
        raise InvalidMessagePayloadError("cannot unpack message from non-dict envelope")

    required_fields = {"message_type", "data"}
    missing_fields = {x for x in required_fields if x not in envelope}
    unknown_fields = {x for x in envelope if x not in required_fields}

    if missing_fields:
        raise InvalidMessagePayloadError(
            f"cannot unpack message missing required envelope fields: {missing_fields}"
        )

    message_type = envelope["message_type"]

    type_errors = []
    if not isinstance(message_type, str):
        type_errors.append("message_type expected str, got " + _typename(message_type))
    if not isinstance(envelope["data"], dict):
        type_errors.append("data expected dict, got " + _typename(envelope["data"]))
    if type_errors:
        raise InvalidMessagePayloadError(
            f"incorrect types for envelope fields: {type_errors}"
        )

    if unknown_fields:
        log.warning(
            "encountered unknown envelope fields while reading a %s message: %s",
            message_type,
            unknown_fields,
        )


class MessagePackProtocolV1(MessagePackProtocol):
    MESSAGE_TYPE_MAP: dict[str, type[Message]] = {}

    def pack(self, message: Message) -> bytes:
        body = {
            "message_type": message.message_type,
            "data": _json_safe_dict(message),
        }
        # encode() converts to bytes, but no characters will actually be altered because
        # ensure_ascii is being used
        # encode() defaults to UTF-8, which is what the protocol specifies
        return (
            _VERSION_BYTE
            + json.dumps(body, separators=(",", ":"), ensure_ascii=True).encode()
        )

    def unpack(self, buf: bytes) -> Message:
        # strip the version byte header
        body = buf[1:]
        envelope = json.loads(body)
        _check_envelope(envelope)

        message_type = envelope["message_type"]
        try:
            message_class = self.MESSAGE_TYPE_MAP[message_type]
        except KeyError as e:
            raise UnrecognizedMessageTypeError(f"message_type={message_type}") from e
        data = envelope["data"]
        return _load_from_json(data, message_class)

    @classmethod
    def register_message_type(cls, message_class: type[Message]) -> None:
        cls.MESSAGE_TYPE_MAP[message_class.message_type] = message_class


for m in ALL_MESSAGE_CLASSES:
    MessagePackProtocolV1.register_message_type(m)
