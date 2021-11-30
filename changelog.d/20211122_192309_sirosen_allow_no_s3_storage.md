### Added

- Add the `funcx_common.task_storage.get_default_task_storage()` method, which
  reads the `FUNCX_REDIS_STORAGE_THRESHOLD` and `FUNCX_S3_BUCKET_NAME` environment
  variables and constructs the appropriate TaskStorage object

  - Detection of S3/Redis vs Redis-only storage is done by the presence/absence
    of the `FUNCX_S3_BUCKET_NAME` variable. It can be forced to redis-only by
    setting `FUNCX_REDIS_STORAGE_THRESHOLD="-1"`
  - The storage threshold has a default value of 20,000 if not set

- Add `funcx_common.task_storage.ImplicitRedisStorage` as a storage class which
  only reads and writes the task object, on the assumption that it is a
  RedisTask

### Changed

- RedisS3Storage now contains an ImplicitRedisStorage object which is used to
  implement read/write to redis
- RedisS3Storage now requires `bucket_name` and `redis_threshold` as
  keyword-only arguments, if constructed directly
