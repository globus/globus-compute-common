import os
import uuid

import boto3
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


@pytest.mark.skipif(
    os.environ.get("AWS_PROFILE") is None,
    reason="Test requires AWS creds until mock is added",
)
def test_s3_storage():
    """Confirm that data is stored to s3"""
    # We are setting threshold of 0 to force only s3 storage
    store = RedisS3Storage(bucket_name="funcx-test-1", redis_threshold=0)
    result = "Hello World!"
    task = SimpleInMemoryTask()

    store.store_result(task, result)
    assert store.get_result(task) == result
    assert task.result_reference
    assert task.result_reference["storage_id"] == "s3"


@pytest.mark.skipif(
    os.environ.get("AWS_PROFILE") is None,
    reason="Test requires AWS creds until mock is added",
)
def test_s3_storage_bad():
    """Confirm exception on bad S3 target"""
    # We are setting threshold of 0 to force only s3 storage
    store = RedisS3Storage(bucket_name="funcx-test-BAD", redis_threshold=0)
    result = "Hello World!"
    task = SimpleInMemoryTask()

    with pytest.raises(StorageException):
        store.store_result(task, result)

    with pytest.raises(StorageException):
        store.get_result(task)


@pytest.mark.skipif(
    os.environ.get("AWS_PROFILE") is None,
    reason="Test requires AWS creds until mock is added",
)
def test_s3_storage_direct():
    """Confirm that data is stored to s3 via boto3"""
    # We are setting threshold of 0 to force only s3 storage
    test_bucket = "funcx-test-1"
    store = RedisS3Storage(bucket_name=test_bucket, redis_threshold=0)
    result = "Hello World!"
    task = SimpleInMemoryTask()

    store.store_result(task, result)

    s3_client = boto3.client("s3")
    response = s3_client.list_objects(Bucket=test_bucket, Prefix=task.task_id)
    assert response["Contents"]
    assert len(response["Contents"]) == 1
