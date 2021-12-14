import uuid

import pytest

from funcx_common.task_storage import RedisS3Storage, StorageException
from funcx_common.tasks import TaskProtocol, TaskState

try:
    import boto3
except ImportError:
    pytest.skip(
        "these tests require the boto3 lib",
        allow_module_level=True,
    )


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
        self.payload = None
        self.payload_reference = None


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


def test_s3_storage_payload(funcx_s3_bucket):
    """Confirm that data is stored to s3"""
    # We are setting threshold of 0 to force only s3 storage
    store = RedisS3Storage(bucket_name=funcx_s3_bucket, redis_threshold=0)
    payload = "Hello World!"
    task = SimpleInMemoryTask()

    store.store_payload(task, payload)
    assert store.get_payload(task) == payload
    assert task.payload_reference
    assert task.payload_reference["storage_id"] == "s3"


def test_s3_storage_below_threshold(funcx_s3_bucket):
    """Confirm that data is NOT stored to s3"""
    store = RedisS3Storage(bucket_name=funcx_s3_bucket, redis_threshold=100)
    data = "Hello World!"
    task = SimpleInMemoryTask()

    store.store_result(task, data)
    assert store.get_result(task) == data
    assert task.result_reference
    assert task.result_reference["storage_id"] == "redis"

    store.store_payload(task, data)
    assert store.get_payload(task) == data
    assert task.payload_reference
    assert task.payload_reference["storage_id"] == "redis"

    # ensure that S3 was not written with data for the task
    s3_client = boto3.client("s3")
    response = s3_client.list_objects(Bucket=funcx_s3_bucket, Prefix=task.task_id)
    assert "Contents" not in response


def test_s3_storage_bad_bucket():
    """Confirm exception on bad S3 target"""

    # generate a random bucket name which is almost certain not to exist
    bucket_name = f"funcx-nonexistent-bucket-{uuid.uuid4().hex}"

    # We are setting threshold of 0 to force only s3 storage
    store = RedisS3Storage(bucket_name=bucket_name, redis_threshold=0)
    data = "Hello World!"
    task = SimpleInMemoryTask()

    with pytest.raises(StorageException):
        store.store_result(task, data)

    with pytest.raises(StorageException):
        store.store_payload(task, data)

    # because writing failed above, no exception will be seen when reading
    # to test that, we must either explicitly delete the task data or the bucket
    # after *successfully* storing the result
    # see the "deleted data" test below for that scenario
    assert store.get_result(task) is None
    assert store.get_payload(task) is None


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


def test_s3_storage_direct_payload(funcx_s3_bucket):
    """Confirm that data is stored to s3 via boto3 for payloads"""
    # We are setting threshold of 0 to force only s3 storage
    store = RedisS3Storage(bucket_name=funcx_s3_bucket, redis_threshold=0)
    data = "Hello World!"
    task = SimpleInMemoryTask()

    store.store_payload(task, data)

    s3_client = boto3.client("s3")
    response = s3_client.list_objects(Bucket=funcx_s3_bucket, Prefix=task.task_id)
    assert response["Contents"]
    assert len(response["Contents"]) == 1


def test_s3_storage_deleted_data(funcx_s3_bucket):
    store = RedisS3Storage(bucket_name=funcx_s3_bucket, redis_threshold=0)
    result = "Hello World!"
    task = SimpleInMemoryTask()

    store.store_result(task, result)

    # explicit delete from S3
    s3_client = boto3.client("s3")
    s3_client.delete_object(
        Bucket=task.result_reference["s3bucket"], Key=task.result_reference["key"]
    )

    with pytest.raises(StorageException) as excinfo:
        store.get_result(task)

    err = excinfo.value
    assert "Fetching object from S3 failed" in str(err)


def test_s3_storage_deleted_payload(funcx_s3_bucket):
    store = RedisS3Storage(bucket_name=funcx_s3_bucket, redis_threshold=0)
    data = "Hello World!"
    task = SimpleInMemoryTask()

    store.store_payload(task, data)

    # explicit delete from S3
    s3_client = boto3.client("s3")
    s3_client.delete_object(
        Bucket=task.payload_reference["s3bucket"], Key=task.payload_reference["key"]
    )

    with pytest.raises(StorageException) as excinfo:
        store.get_payload(task)

    err = excinfo.value
    assert "Fetching object from S3 failed" in str(err)
