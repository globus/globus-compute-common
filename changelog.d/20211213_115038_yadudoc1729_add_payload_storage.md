### Added

- `funcx_common.task_storage.TaskStorage` and its child classes (`ImplicitRedisStorage` and
    `RedisS3Storage`) now support `store_payload` and `get_payload` methods.
- `Kind` enum to represent `result` and `payload` types.


### Changed

- `funcx_common.task_storage.RedisS3Storage`'s `_store_to_s3` and `_get_from_s3` method
    signatures have been updated to use a `kind: {"result", "payload"}` option so that the
    same method can be used for both results and payloads.

