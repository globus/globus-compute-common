### Removed

- NullTaskStorage
- ChainedTaskStorage
- MemoryTaskStorage
- ThresholdedMemoryTaskStorage
- RedisTaskStorage
- ThresholdedRedisTaskStorage
- S3TaskStorage

### Added

- RedisS3Storage

### Changed

- TaskStorage base class has been stripped down to require only store_result and get_result
