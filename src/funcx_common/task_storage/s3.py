import typing as t
from enum import Enum

try:
    import boto3
    import botocore.exceptions

    has_boto3 = True
except ImportError:
    has_boto3 = False

from ..tasks import TaskProtocol
from .base import StorageException, TaskStorage
from .redis import ImplicitRedisStorage


class StorageFieldName(Enum):
    result = "result"
    payload = "payload"

    @property
    def reference_attr(self) -> str:
        return f"{self.value}_reference"


class RedisS3Storage(TaskStorage):
    """
    Abstract storage over Redis and S3.
    Uses Redis to store objects below of size threshold, and S3 for the rest
    """

    def __init__(self, *, bucket_name: str, redis_threshold: int) -> None:
        """
        :param bucket_name: Name of the S3 bucket to use
        :param redis_threshold: Max size(chars) of the data that redis accommodates
        """

        if not has_boto3:
            raise RuntimeError(
                "Cannot construct RedisS3Storage object since the boto3"
                "package is not available. Either install it explicitly or install the "
                "'boto3' extra, as in\n"
                "  pip install 'funcx-common[boto3]'"
            )

        self.bucket_name = bucket_name
        self.client = boto3.client("s3")

        self.redis_threshold = redis_threshold
        self.redis_storage = ImplicitRedisStorage()

    def _store_to_s3(
        self, task: TaskProtocol, storage_field_name: StorageFieldName, result: str
    ) -> None:

        key = f"{task.task_id}.{storage_field_name.reference_attr}"
        try:
            self.client.put_object(
                Body=result.encode("utf-8"),
                Bucket=self.bucket_name,
                Key=key,
            )
        except botocore.exceptions.ClientError as err:
            raise StorageException(
                f"Putting {storage_field_name.reference_attr} into s3 for "
                f"task:{task.task_id} failed"
            ) from err
        else:
            reference = {
                "storage_id": "s3",
                "s3bucket": self.bucket_name,
                "key": key,
            }
            setattr(task, storage_field_name.reference_attr, reference)

    def _get_from_s3(
        self, task: TaskProtocol, storage_field_name: StorageFieldName
    ) -> str:

        reference = getattr(task, storage_field_name.reference_attr)
        if reference is None:  # pragma: no cover
            raise StorageException(
                f"task {task.task_id} result reference was None inside of _get_from_s3"
            )
        try:
            bucket = reference["s3bucket"]
            key = reference["key"]
        except KeyError as err:
            raise StorageException(
                f"task {task.task_id} {storage_field_name.reference_attr} "
                "pointed to S3, but was missing s3bucket or key"
            ) from err

        if not isinstance(bucket, str):
            raise StorageException(
                f"task {task.task_id} {storage_field_name.reference_attr} "
                f"pointed to S3, but s3bucket was of type {type(bucket)}, "
                "(expected string)"
            )

        if not isinstance(key, str):
            raise StorageException(
                f"task {task.task_id} {storage_field_name.reference_attr} "
                f"pointed to S3, but key was of type {type(key)} (expected string)"
            )

        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
        except botocore.exceptions.ClientError as err:
            raise StorageException(
                f"Fetching object from S3 failed for: {task.task_id}"
            ) from err
        body = response["Body"]
        return t.cast(str, body.read().decode("utf-8"))

    def store_result(
        self,
        task: TaskProtocol,
        result: str,
    ) -> None:
        if len(result) > self.redis_threshold:
            # Task is too big for Redis, store in S3
            self._store_to_s3(task, StorageFieldName.result, result)
        else:
            self.redis_storage.store_result(task, result)

    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        """

        :param task:
        :return: Results result if available, else returns None
        Raises StorageException if fetching fails
        """
        # We should be able to safely remove the following block
        # once all tasks launched with v0.3.3 and prior have TTL'ed out
        if task.result:
            return task.result

        if task.result_reference:
            if task.result_reference["storage_id"] == "s3":
                return self._get_from_s3(task, StorageFieldName.result)

            # The following is redundant now while the block above
            # for backward compat exists
            # remove the pragma once this is an active codepath
            elif task.result_reference["storage_id"] == "redis":  # pragma: no cover
                return self.redis_storage.get_result(task)
            else:
                raise StorageException(
                    f"Unknown Storage requested: {task.result_reference}"
                )
        else:
            return None

    def store_payload(self, task: TaskProtocol, payload: str) -> None:
        if len(payload) > self.redis_threshold:
            # Task is too big for Redis, store in S3
            self._store_to_s3(task, StorageFieldName.payload, payload)
        else:
            self.redis_storage.store_payload(task, payload)

    def get_payload(self, task: TaskProtocol) -> t.Optional[str]:
        """

        :param task:
        :return: Results payload if available, else returns None
        Raises StorageException if fetching fails
        """
        # We should be able to safely remove the following block
        # once all tasks launched with v0.3.3 and prior have TTL'ed out
        if task.payload:
            return task.payload

        if task.payload_reference:
            if task.payload_reference["storage_id"] == "s3":
                return self._get_from_s3(task, StorageFieldName.payload)

            # The following is redundant now while the block above
            # for backward compat exists
            # remove the pragma once this is an active codepath
            elif task.payload_reference["storage_id"] == "redis":  # pragma: no cover
                return self.redis_storage.get_payload(task)
            else:
                raise StorageException(
                    f"Unknown Storage requested: {task.payload_reference}"
                )
        else:
            return None
