import typing as t

try:
    import boto3

    has_boto3 = True
except ImportError:
    has_boto3 = False

from ..tasks import TaskProtocol
from .base import StorageException, TaskStorage


class S3TaskStorage(TaskStorage):
    """
    Store Task data in S3

    """

    storage_id = "S3TaskStorage"

    def __init__(self, bucket_name: str) -> None:

        if not has_boto3:
            raise RuntimeError(
                "Cannot construct S3TaskStorage object since the boto3"
                "package is not available. Either install it explicitly or install the "
                "'boto3' extra, as in\n"
                "  pip install 'funcx-common[boto3]'"
            )

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
            raise StorageException(f"Task Result was not stored with {self.storage_id}")
