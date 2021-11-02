import typing as t

import boto3

from ..tasks import TaskProtocol
from .base import StorageException, TaskStorage


class S3TaskStorage(TaskStorage):
    """
    Store Task data in S3

    """

    storage_id = "MemoryTaskStorage"

    def __init__(self, bucket_name: str) -> None:
        self.bucket_name = bucket_name
        self.client = boto3.client("s3")
        self._results: t.Dict[str, str] = {}

    def store_result(
        self, task: TaskProtocol, result: str, ACL: str = "authenticated"
    ) -> bool:
        key = f"{task.task_id}.result"
        self.client.put_object(  # ACL=ACL,
            Body=result.encode("utf-8"),
            Bucket=self.bucket_name,
            Key=key,
        )
        task.result_reference = {
            "storage_id": self.storage_id,
            "s3bucket": self.bucket_name,
            "key": key,
        }
        return True

    def get_result(self, task: TaskProtocol) -> t.Optional[str]:
        if (
            task.result_reference
            and task.result_reference["storage_id"] == self.storage_id
        ):
            response = self.client.get_object(
                Bucket=task.result_reference["s3bucket"],
                Key=task.result_reference["key"],
            )
            # mypy seems to think that the following line does not return a string
            return response["Body"].read().decode("utf-8")  # type: ignore
        else:
            raise StorageException("Task Result was not stored with MemoryTaskStorage")
