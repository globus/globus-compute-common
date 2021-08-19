import enum
import json
import typing as t


class FuncxRedisSerde:
    """
    A Serializer/Deserializer for data going into or out of Redis.

    The base implementation just stringifies data and does nothing when
    deserializing.
    """

    def serialize(self, value: t.Any) -> str:
        return str(value)

    def deserialize(self, value: str) -> t.Any:
        return value


class FuncxRedisIntSerde(FuncxRedisSerde):
    def deserialize(self, value: str) -> int:
        try:
            return int(value)
        except ValueError as e:
            raise ValueError(
                f"Invalid int value when loading from Redis: {value}"
            ) from e


class FuncxRedisJSONSerde(FuncxRedisSerde):
    def serialize(self, value: t.Any) -> str:
        return json.dumps(value)

    def deserialize(self, value: str) -> t.Any:
        return json.loads(value)


class FuncxRedisEnumSerde(FuncxRedisSerde):
    def __init__(self, enum_class: t.Type[enum.Enum]) -> None:
        self.enum_class = enum_class

    def serialize(self, value: t.Any) -> str:
        return str(value.value)

    def deserialize(self, value: str) -> t.Any:
        return self.enum_class(value)


DEFAULT_SERDE = FuncxRedisSerde()
INT_SERDE = FuncxRedisIntSerde()
JSON_SERDE = FuncxRedisJSONSerde()
