### Removed

- `funcx_common.redis.HasRedisConnection` no longer provides the
  `log_connection_errors` decorator
- `funcx_common.redis.FuncxRedisPubSub` and `funcx_common.redis.FuncxEndpointTaskQueue`
  no longer automatically log redis connection errors to the `funcx_common` logger. Users
  of these classes should either handle these errors themselves or make use of the new
  error logging decorator

### Added

- A `funcx_common.redis.HasRedisConnection` object now accepts a
  `redis_connection_factory` callable which is used to instantiate the `redis.Redis`
  object, to allow overrides to the connection construction process. The callable
  must have the signature `(str, int) -> redis.Redis`, and the default
  is a function visible under the name
  `funcx_common.redis.default_redis_connection_factory`.
- A new context-manager is available as a method of the `HasRedisConnection` class,
  `HasRedisConnection.connection_error_logging`. This can be used to capture
  and log (at exception-level) redis connection errors to the `funcx_common` logger
- The default connection construction for `HasRedisConnection` now sets
  `health_check_interval=30`. To override this setting, use
  `redis_connection_factory`

### Changed

- The `FuncxRedisConnection` class has been renamed to
  `HasRedisConnection`. The name change better indicates that this class
  is not a connection itself -- it's just an inheritable way of constructing
  a connection.
