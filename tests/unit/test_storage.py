import uuid

import pytest

from funcx_common.task_storage import (
    ImplicitRedisStorage,
    RedisS3Storage,
    StorageException,
    get_default_task_storage,
)
from funcx_common.tasks import TaskProtocol, TaskState

try:
    import boto3
    from moto import mock_s3

    has_boto = True
except ImportError:
    has_boto = False


class SimpleInMemoryTask(TaskProtocol):
    def __init__(self):
        self.task_id = str(uuid.uuid1())
        self.endpoint = None
        self.status = TaskState.RECEIVED
        self.result = None
        self.result_reference = None


@pytest.fixture
def test_bucket_mock():
    with mock_s3():
        res = boto3.client("s3")
        res.create_bucket(Bucket="funcx-test-1")
        yield


@pytest.mark.skipif(not has_boto, reason="test requires boto3 lib")
def test_default_task_storage_s3(funcx_s3_bucket, monkeypatch):
    monkeypatch.setenv("FUNCX_S3_BUCKET_NAME", funcx_s3_bucket)
    monkeypatch.delenv("FUNCX_REDIS_STORAGE_THRESHOLD", raising=False)

    store = get_default_task_storage()
    assert isinstance(store, RedisS3Storage)
    assert store.redis_threshold == 20000  # default value

    # now set a threshold and confirm it gets picked up
    monkeypatch.setenv("FUNCX_REDIS_STORAGE_THRESHOLD", "100")
    store = get_default_task_storage()
    assert isinstance(store, RedisS3Storage)
    assert store.redis_threshold == 100

    # now set an invalid threshold value; confirm that it is ignored
    monkeypatch.setenv("FUNCX_REDIS_STORAGE_THRESHOLD", "foo")
    store = get_default_task_storage()
    assert isinstance(store, RedisS3Storage)
    assert store.redis_threshold == 20000  # default value


def test_default_task_storage_redis(monkeypatch):
    # no env vars set -> ImplicitRedisStorage
    monkeypatch.delenv("FUNCX_S3_BUCKET_NAME", raising=False)
    monkeypatch.delenv("FUNCX_REDIS_STORAGE_THRESHOLD", raising=False)

    store = get_default_task_storage()
    assert isinstance(store, ImplicitRedisStorage)

    # confirm that setting a threshold does not change behavior
    # (because bucket is not set)
    monkeypatch.setenv("FUNCX_REDIS_STORAGE_THRESHOLD", "100")
    store = get_default_task_storage()
    assert isinstance(store, ImplicitRedisStorage)


# this test technically doesn't need to have boto3 installed, but requiring it ensures
# that in the failure case, we will get clearer messages
@pytest.mark.skipif(not has_boto, reason="test requires boto3 lib")
def test_default_task_storage_redis_from_threshold(funcx_s3_bucket, monkeypatch):
    # bucket=... but threshold=-1 -> ImplicitRedisStorage
    monkeypatch.setenv("FUNCX_S3_BUCKET_NAME", funcx_s3_bucket)
    monkeypatch.setenv("FUNCX_REDIS_STORAGE_THRESHOLD", "-1")

    store = get_default_task_storage()
    assert isinstance(store, ImplicitRedisStorage)


@pytest.mark.skipif(not has_boto, reason="test requires boto3 lib")
def test_storage_simple(funcx_s3_bucket):
    # We are setting threshold of 1000 to force storage into redis
    store = RedisS3Storage(bucket_name=funcx_s3_bucket, redis_threshold=1000)
    result = "Hello World!"
    task = SimpleInMemoryTask()

    store.store_result(task, result)
    assert store.get_result(task) == result
    assert task.result == result
    assert task.result_reference
    assert task.result_reference["storage_id"] == "redis"


@pytest.mark.skipif(not has_boto, reason="test requires boto3 lib")
def test_backward_compat(funcx_s3_bucket):
    store = RedisS3Storage(bucket_name=funcx_s3_bucket, redis_threshold=1000)
    result = "Hello World!"
    task = SimpleInMemoryTask()
    task.result = result

    assert store.get_result(task) == result


@pytest.mark.xfail(reason="This will fail until we remove backward compat support")
def test_bad_reference(funcx_s3_bucket):
    store = RedisS3Storage(bucket_name=funcx_s3_bucket, redis_threshold=1000)
    result = "Hello World!"
    task = SimpleInMemoryTask()
    task.result = result

    # task.result_reference = {'storage_id': 'BAD'}
    print(store.get_result(task))
    with pytest.raises(StorageException):
        store.get_result(task)


@pytest.mark.skipif(not has_boto, reason="test requires boto3 lib")
def test_no_result(funcx_s3_bucket):
    """Confirm get_result returns None when there's no result"""
    # We are setting threshold of 0 to force only s3 storage
    store = RedisS3Storage(bucket_name=funcx_s3_bucket, redis_threshold=0)
    task = SimpleInMemoryTask()

    assert store.get_result(task) is None


@pytest.mark.skipif(has_boto, reason="test only runs without boto3 lib")
def test_cannot_create_storage_without_boto3_lib(funcx_s3_bucket):
    with pytest.raises(RuntimeError):
        # can't create a storage
        RedisS3Storage(bucket_name=funcx_s3_bucket, redis_threshold=0)


@pytest.mark.skipif(not has_boto, reason="test requires boto3 lib")
def test_s3_storage_simple(test_bucket_mock):
    """Confirm that data is stored to s3(mock)"""
    # We are setting threshold of 0 to force only s3 storage
    store = RedisS3Storage(bucket_name="funcx-test-1", redis_threshold=0)
    result = "Hello World!"
    task = SimpleInMemoryTask()

    store.store_result(task, result)
    assert store.get_result(task) == result
    assert task.result_reference
    assert task.result_reference["storage_id"] == "s3"


@pytest.mark.skipif(not has_boto, reason="test requires boto3 lib")
def test_differentiator(test_bucket_mock):
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


@pytest.mark.skipif(not has_boto, reason="test requires boto3 lib")
@pytest.mark.parametrize(
    "storage_attrs",
    [
        {"s3bucket": {"do": "del"}, "key": {"do": "del"}},
        {"s3bucket": {"do": "del"}},
        {"key": {"do": "del"}},
        {"s3bucket": {"do": "set", "val": None}},
        {"key": {"do": "set", "val": None}},
    ],
)
def test_s3_task_with_invalid_reference(test_bucket_mock, storage_attrs):
    store = RedisS3Storage(bucket_name="funcx-test-1", redis_threshold=0)

    result = "Hello World!"
    task = SimpleInMemoryTask()
    store.store_result(task, result)

    assert task.result_reference["storage_id"] == "s3"
    for key, action in storage_attrs.items():
        if action["do"] == "del":
            del task.result_reference[key]
        elif action["do"] == "set":
            task.result_reference[key] = action["val"]

    with pytest.raises(StorageException):
        store.get_result(task)


@pytest.mark.skipif(not has_boto, reason="test requires boto3 lib")
def test_task_with_unknown_storage(test_bucket_mock):
    store = RedisS3Storage(bucket_name="funcx-test-1", redis_threshold=0)

    result = "Hello World!"
    task = SimpleInMemoryTask()
    store.store_result(task, result)
    assert task.result_reference["storage_id"] == "s3"
    task.result_reference["storage_id"] = "UnknownFakeStorageType"

    with pytest.raises(StorageException):
        store.get_result(task)


def test_storage_exception_str():
    err = StorageException("foo")
    assert str(err).endswith("reason: foo")
