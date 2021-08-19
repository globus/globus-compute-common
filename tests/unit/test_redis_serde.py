import pytest

from funcx_common.redis import DEFAULT_SERDE, INT_SERDE, JSON_SERDE, FuncxRedisEnumSerde
from funcx_common.tasks import TaskState


def test_basic_serde():
    assert DEFAULT_SERDE.serialize("foo") == "foo"
    assert DEFAULT_SERDE.deserialize(DEFAULT_SERDE.serialize("foo")) == "foo"
    assert DEFAULT_SERDE.serialize(1) == "1"
    assert DEFAULT_SERDE.deserialize(DEFAULT_SERDE.serialize(1)) == "1"


def test_int_serde():
    assert INT_SERDE.serialize(1) == "1"
    assert INT_SERDE.deserialize(INT_SERDE.serialize(1)) == 1

    with pytest.raises(ValueError):
        INT_SERDE.deserialize("1.0")


def test_json_serde():
    assert JSON_SERDE.serialize(1) == "1"
    assert JSON_SERDE.deserialize(JSON_SERDE.serialize(1)) == 1

    assert isinstance(JSON_SERDE.serialize({"a": 1, "b": ["c", "d"]}), str)
    assert JSON_SERDE.deserialize(JSON_SERDE.serialize({"a": 1, "b": ["c", "d"]})) == {
        "a": 1,
        "b": ["c", "d"],
    }


def test_enum_serde():
    serde = FuncxRedisEnumSerde(TaskState)
    assert serde.serialize(TaskState.RUNNING) == "running"
    assert serde.deserialize(serde.serialize(TaskState.RUNNING)) is TaskState.RUNNING
