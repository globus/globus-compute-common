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

  - if a payload does not contain a required field, loading will fail with a
    pydantic ValidationError

  - if a payload defines fields which are not included in the current message
    definitions, they are ignored and a warning is logged

  - if an envelope includes unknown fields (other than "message_type" and "data"), they
    are ignored and a warning is logged

Therefore, new fields may be added to the message classes, but they must not be
required until all messages contain those fields.
"""  # noqa: E501
from __future__ import annotations

import json
import logging
import typing as t

import pydantic

from ..message_types import ALL_MESSAGE_CLASSES, Message
from ..protocol import MessagePackProtocol

log = logging.getLogger(__name__)

# protocol version and reserved byte as a byte array
_VERSION_BYTE = (1).to_bytes(1, byteorder="big", signed=False)

# internal to this module, a mapping from message classes to their names
_MESSAGE_TYPE_MAP: dict[str, type[Message]] = {
    m.Meta.message_type: m for m in ALL_MESSAGE_CLASSES
}


class MessageEnvelope(pydantic.BaseModel):
    message_type: str
    data: t.Dict[str, t.Any]

    @pydantic.validator("message_type")
    def message_type_is_known(cls, v: str) -> str:
        if v not in _MESSAGE_TYPE_MAP:
            # pydantic will wrap this message + context in a ValidationError
            raise ValueError("unrecognized value")
        return v


_ModelT = t.TypeVar("_ModelT", bound=t.Union[Message, MessageEnvelope])


def _log_unknown_fields(model: type[_ModelT], data: dict[str, t.Any]) -> None:
    if issubclass(model, MessageEnvelope):
        outer_type = "envelope"
        message_type = data["message_type"]
    elif issubclass(model, Message):
        outer_type = "data"
        message_type = model.Meta.message_type
    else:
        raise NotImplementedError

    model_ = t.cast("type[pydantic.BaseModel]", model)
    unknown_fields = {x for x in data if x not in model_.__fields__}
    if unknown_fields:
        log.warning(
            "encountered unknown %s fields while reading a %s message: %s",
            outer_type,
            message_type,
            unknown_fields,
        )


def _load(model: type[_ModelT], data: dict[str, t.Any]) -> _ModelT:
    model_ = t.cast("type[pydantic.BaseModel]", model)
    ret = model_.parse_obj(data)
    _log_unknown_fields(model, data)
    return t.cast(_ModelT, ret)


class MessagePackProtocolV1(MessagePackProtocol):
    def pack(self, message: Message) -> bytes:
        body = MessageEnvelope(message_type=message.message_type, data=message.dict())
        # encode() defaults to UTF-8, which is what the protocol specifies
        return _VERSION_BYTE + body.json(separators=(",", ":")).encode()

    def unpack(self, buf: bytes) -> Message:
        # strip the version byte header
        body = buf[1:]
        payload = json.loads(body)
        envelope = _load(MessageEnvelope, payload)

        message_class = _MESSAGE_TYPE_MAP[envelope.message_type]
        message = _load(message_class, envelope.data)
        return message
