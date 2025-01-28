import enum
import json
import typing as t
import uuid


class ComputeRedisSerde:
    """
    A Serializer/Deserializer for data going into or out of Redis.

    The base implementation just stringifies data and does nothing when
    deserializing.
    """

    def serialize(self, value: t.Any) -> str:
        return str(value)

    def deserialize(self, value: str) -> t.Any:
        return value


class ComputeRedisIntSerde(ComputeRedisSerde):
    def deserialize(self, value: str) -> int:
        try:
            return int(value)
        except ValueError as e:
            raise ValueError(
                f"Invalid int value when loading from Redis: {value}"
            ) from e


class ComputeRedisFloatSerde(ComputeRedisSerde):
    def deserialize(self, value: str) -> float:
        try:
            return float(value)
        except ValueError as e:
            raise ValueError(
                f"Invalid float value when loading from Redis: {value}"
            ) from e


class ComputeRedisJSONSerde(ComputeRedisSerde):
    def serialize(self, value: t.Any) -> str:
        return json.dumps(value)

    def deserialize(self, value: str) -> t.Any:
        return json.loads(value)


class ComputeRedisEnumSerde(ComputeRedisSerde):
    def __init__(self, enum_class: t.Type[enum.Enum]) -> None:
        self.enum_class = enum_class

    def serialize(self, value: t.Any) -> str:
        return str(value.value)

    def deserialize(self, value: str) -> t.Any:
        return self.enum_class(value)


class ComputeRedisUUIDSerde(ComputeRedisSerde):
    def deserialize(self, value: str) -> t.Any:
        try:
            return uuid.UUID(value)
        except ValueError as e:
            raise ValueError(
                f"Invalid UUID value when loading from Redis: {value}"
            ) from e


DEFAULT_SERDE = ComputeRedisSerde()
INT_SERDE = ComputeRedisIntSerde()
FLOAT_SERDE = ComputeRedisFloatSerde()
JSON_SERDE = ComputeRedisJSONSerde()
UUID_SERDE = ComputeRedisUUIDSerde()
