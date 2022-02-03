from __future__ import annotations

import typing as t
import uuid
from dataclasses import asdict, dataclass, fields

from .validators import get_validator


def _convert_json_unsafe(data: t.Any) -> t.Any:
    if isinstance(data, dict):
        return {k: _convert_json_unsafe(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_convert_json_unsafe(x) for x in data]
    elif isinstance(data, uuid.UUID):
        return str(data)
    else:
        return data


@dataclass
class Message:
    message_type: t.ClassVar[str]

    def __post_init__(self) -> None:
        for field_obj in fields(self):
            validator = get_validator(field_obj)
            if validator:
                validator(self, field_obj.name)

    def get_json_safe_dict(self) -> dict[str, t.Any]:
        return t.cast(t.Dict[str, t.Any], _convert_json_unsafe(asdict(self)))
