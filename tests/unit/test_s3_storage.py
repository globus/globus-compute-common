import uuid

import boto3
import pytest
from moto import mock_s3

from funcx_common.task_storage import RedisS3Storage
from funcx_common.tasks import TaskProtocol, TaskState


class SimpleInMemoryTask(TaskProtocol):
    def __init__(self):
        self.task_id = str(uuid.uuid1())
        self.endpoint = None
        self.status = TaskState.RECEIVED
        self.result = None
        self.result_reference = None


@pytest.fixture()
def test_bucket_mock():
    with mock_s3():
        res = boto3.client("s3")
        res.create_bucket(Bucket="funcx-test-1")
        yield


@pytest.mark.usefixtures("test_bucket_mock")
def test_s3_storage_simple():
    """Confirm that data is stored to s3(mock)"""
    # We are setting threshold of 0 to force only s3 storage
    store = RedisS3Storage(bucket_name="funcx-test-1", redis_threshold=0)
    result = "Hello World!"
    task = SimpleInMemoryTask()

    store.store_result(task, result)
    assert store.get_result(task) == result
    assert task.result_reference
    assert task.result_reference["storage_id"] == "s3"


@pytest.mark.usefixtures("test_bucket_mock")
def test_differentiator():
    """Confirm that the threshold works to pick the right storage target"""
    # We are setting threshold of 0 to force only s3 storage
    store = RedisS3Storage(bucket_name="funcx-test-1", redis_threshold=5)

    result1 = "Hi"
    result2 = "Hello World!"
    task1 = SimpleInMemoryTask()
    task2 = SimpleInMemoryTask()

    store.store_result(task1, result1)
    store.store_result(task2, result2)

    assert store.get_result(task1) == result1
    assert task1.result == result1
    assert task1.result_reference["storage_id"] == "redis"

    assert store.get_result(task2) == result2
    assert task2.result_reference["storage_id"] == "s3"
