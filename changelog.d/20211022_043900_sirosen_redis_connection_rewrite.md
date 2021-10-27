### Removed

- The `HasRedisConnection` class has been removed

### Added

- Redis connections created by `default_redis_connection_factory` now default
  to loading a redis URL from an environment variable, `FUNCX_COMMON_REDIS_URL`,
  with a default of `redis://localhost:6379`

### Changed

- The redis logging decorator has been moved. It is no longer attached to a
  class, but is now available as `funcx_common.redis.redis_connection_error_logging`
- The signatures for creating `FuncxRedisPubSub` and `FuncxEndpointTaskQueue`
  have changed. They can now be passed a `redis.Redis` object, and default to
  calling `default_redis_connection_factory`
