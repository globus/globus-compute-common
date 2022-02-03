from __future__ import annotations

import typing as t
import uuid
from dataclasses import Field

from .exceptions import InvalidMessageError

ValidatorType = t.Callable[[t.Any, str], None]


def _validate_str_or_uuid_field(msg: t.Any, field_name: str) -> None:
    val = getattr(msg, field_name)
    if not isinstance(val, uuid.UUID):
        try:
            uuid.UUID(val)
        except (ValueError, TypeError) as e:
            raise InvalidMessageError(
                f"{msg.message_type} message field '{field_name}' "
                "does not appear to be a UUID"
            ) from e


def get_validator(field_obj: Field[t.Any]) -> ValidatorType | None:
    if field_obj.type in TYPE_MAPPING:
        return TYPE_MAPPING[field_obj.type]
    return None


TYPE_MAPPING: dict[t.Any, ValidatorType] = {
    t.Union[str, uuid.UUID]: _validate_str_or_uuid_field,
    "str | UUID": _validate_str_or_uuid_field,
    "str | uuid.UUID": _validate_str_or_uuid_field,
}
