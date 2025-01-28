import uuid

import pytest

from globus_compute_common.redis import (
    DEFAULT_SERDE,
    INT_SERDE,
    JSON_SERDE,
    UUID_SERDE,
    ComputeRedisEnumSerde,
)
from globus_compute_common.tasks import TaskState


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
    serde = ComputeRedisEnumSerde(TaskState)
    assert serde.serialize(TaskState.RUNNING) == "running"
    assert serde.deserialize(serde.serialize(TaskState.RUNNING)) is TaskState.RUNNING


def test_uuid_serde():
    uuid_obj = uuid.uuid4()
    uuid_str = str(uuid_obj)
    assert UUID_SERDE.serialize(uuid_obj) == uuid_str
    assert UUID_SERDE.deserialize(uuid_str) == uuid_obj

    with pytest.raises(ValueError) as exc_info:
        UUID_SERDE.deserialize("not-a-uuid")
    assert "Invalid UUID" in str(exc_info.value)
