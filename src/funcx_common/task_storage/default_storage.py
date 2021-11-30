import os
import typing as t

from .base import TaskStorage
from .redis import ImplicitRedisStorage
from .s3 import RedisS3Storage

DEFAULT_REDIS_STORAGE_THRESHOLD: int = 20000


def _get_redis_storage_threshold() -> int:
    val = os.getenv("FUNCX_REDIS_STORAGE_THRESHOLD")
    if val is not None:
        try:
            return int(val)
        except ValueError as err:
            raise ValueError(
                f"could not parse FUNCX_REDIS_STORAGE_THRESHOLD={val} as int"
            ) from err
    return DEFAULT_REDIS_STORAGE_THRESHOLD


def _s3_bucket_name() -> t.Optional[str]:
    return os.getenv("FUNCX_S3_BUCKET_NAME")


def get_default_task_storage() -> TaskStorage:
    bucket = _s3_bucket_name()
    threshold = _get_redis_storage_threshold()

    # a redis threshold of -1 means "never use S3, just use Redis"
    if bucket is None or threshold == -1:
        return ImplicitRedisStorage()
    else:
        return RedisS3Storage(
            bucket_name=bucket, redis_threshold=_get_redis_storage_threshold()
        )
