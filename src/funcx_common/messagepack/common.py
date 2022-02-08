from __future__ import annotations

import typing as t
import uuid
from dataclasses import Field, dataclass, fields

from .exceptions import InvalidMessageError


def is_uuid_field(field_obj: Field[t.Any]) -> bool:
    return t.cast(str, field_obj.type) == "uuid.UUID"


def _validate_uuid_field(msg: t.Any, field_name: str) -> None:
    val = getattr(msg, field_name)
    if not isinstance(val, uuid.UUID):
        raise InvalidMessageError(
            f"{msg.message_type} message field '{field_name}' "
            "does not appear to be a UUID"
        )


@dataclass
class Message:
    message_type: t.ClassVar[str]

    def __post_init__(self) -> None:
        for field_obj in fields(self):
            if is_uuid_field(field_obj):
                _validate_uuid_field(self, field_obj.name)
