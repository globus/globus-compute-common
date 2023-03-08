import uuid

from globus_compute_common.task_storage import ImplicitRedisStorage
from globus_compute_common.tasks import TaskProtocol, TaskState


class SimpleInMemoryTask(TaskProtocol):
    def __init__(self):
        self.task_id = str(uuid.uuid1())
        self.endpoint = None
        self.status = TaskState.RECEIVED
        self.result = None
        self.result_reference = None


def test_implicit_redis_no_result():
    store = ImplicitRedisStorage()
    task = SimpleInMemoryTask()

    assert store.get_result(task) is None


def test_implicit_redis_roundtrip_data():
    store = ImplicitRedisStorage()
    task = SimpleInMemoryTask()

    assert store.get_result(task) is None
    store.store_result(task, "foo")

    assert task.result == "foo"
    assert isinstance(task.result_reference, dict)
    assert "storage_id" in task.result_reference
    assert task.result_reference["storage_id"] == "redis"

    result = store.get_result(task)
    assert result == "foo"
