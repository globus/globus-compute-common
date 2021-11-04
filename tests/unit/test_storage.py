import uuid

import pytest

from funcx_common.task_storage import RedisS3Storage, StorageException
from funcx_common.tasks import TaskProtocol, TaskState


class SimpleInMemoryTask(TaskProtocol):
    def __init__(self):
        self.task_id = str(uuid.uuid1())
        self.endpoint = None
        self.status = TaskState.RECEIVED
        self.result = None
        self.result_reference = None


def test_storage_simple():
    # We are setting threshold of 1000 to force storage into redis
    store = RedisS3Storage(bucket_name="funcx-test-1", redis_threshold=1000)
    result = "Hello World!"
    task = SimpleInMemoryTask()

    store.store_result(task, result)
    assert store.get_result(task) == result
    assert task.result == result
    assert task.result_reference
    assert task.result_reference["storage_id"] == "redis"


def test_backward_compat():
    store = RedisS3Storage(bucket_name="funcx-test-1", redis_threshold=1000)
    result = "Hello World!"
    task = SimpleInMemoryTask()
    task.result = result

    assert store.get_result(task) == result


@pytest.mark.xfail(reason="This will fail until we remove backward compat support")
def test_bad_reference():
    store = RedisS3Storage(bucket_name="funcx-test-1", redis_threshold=1000)
    result = "Hello World!"
    task = SimpleInMemoryTask()
    task.result = result

    # task.result_reference = {'storage_id': 'BAD'}
    print(store.get_result(task))
    with pytest.raises(StorageException):
        store.get_result(task)


def test_no_result():
    """Confirm get_result returns None when there's no result"""
    # We are setting threshold of 0 to force only s3 storage
    store = RedisS3Storage(bucket_name="funcx-test-1", redis_threshold=0)
    task = SimpleInMemoryTask()

    assert store.get_result(task) is None
