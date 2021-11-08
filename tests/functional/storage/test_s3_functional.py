import uuid

import pytest

from funcx_common.task_storage import RedisS3Storage, StorageException
from funcx_common.tasks import TaskProtocol, TaskState

try:
    import boto3

    has_boto = True
except ImportError:
    has_boto = False


@pytest.fixture(autouse=True)
def _requires_s3_bucket(funcx_s3_bucket):
    if not funcx_s3_bucket:
        pytest.skip("test requires --funcx-s3-bucket")


class SimpleInMemoryTask(TaskProtocol):
    def __init__(self):
        self.task_id = str(uuid.uuid1())
        self.endpoint = None
        self.status = TaskState.RECEIVED
        self.result = None
        self.result_reference = None


@pytest.mark.skipif(not has_boto, reason="Test requires boto3 lib")
def test_s3_storage(funcx_s3_bucket):
    """Confirm that data is stored to s3"""
    # We are setting threshold of 0 to force only s3 storage
    store = RedisS3Storage(bucket_name=funcx_s3_bucket, redis_threshold=0)
    result = "Hello World!"
    task = SimpleInMemoryTask()

    store.store_result(task, result)
    assert store.get_result(task) == result
    assert task.result_reference
    assert task.result_reference["storage_id"] == "s3"


@pytest.mark.skipif(not has_boto, reason="Test requires boto3 lib")
def test_s3_storage_bad():
    """Confirm exception on bad S3 target"""

    # generate a random bucket name which is almost certain not to exist
    bucket_name = f"funcx-nonexistent-bucket-{uuid.uuid4().hex}"

    # We are setting threshold of 0 to force only s3 storage
    store = RedisS3Storage(bucket_name=bucket_name, redis_threshold=0)
    result = "Hello World!"
    task = SimpleInMemoryTask()

    with pytest.raises(StorageException):
        store.store_result(task, result)

    # because writing failed above, no exception will be seen when reading
    # to test that, we must either explicitly delete the task data or the bucket
    # after *successfully* storing the result
    assert store.get_result(task) is None


@pytest.mark.skipif(not has_boto, reason="Test requires boto3 lib")
def test_s3_storage_direct(funcx_s3_bucket):
    """Confirm that data is stored to s3 via boto3"""
    # We are setting threshold of 0 to force only s3 storage
    store = RedisS3Storage(bucket_name=funcx_s3_bucket, redis_threshold=0)
    result = "Hello World!"
    task = SimpleInMemoryTask()

    store.store_result(task, result)

    s3_client = boto3.client("s3")
    response = s3_client.list_objects(Bucket=funcx_s3_bucket, Prefix=task.task_id)
    assert response["Contents"]
    assert len(response["Contents"]) == 1
