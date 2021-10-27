# Changelog

<!-- scriv-insert-here -->

## 0.0.8 (2021-10-27)

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

## 0.0.7 (2021-10-22)

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

- Begin using `scriv` to manage the changelog
- The `FuncxRedisConnection` class has been renamed to
  `HasRedisConnection`. The name change better indicates that this class
  is not a connection itself -- it's just an inheritable way of constructing
  a connection.

## 0.0.6 (2021-09-20)

- Add `FuncxRedisPubSub`, which provides a pubsub wrapper over the
  `redis` library's `PubSub` client

## 0.0.5 (2021-08-23)

- Fix mypy type inference on RedisField descriptors

## 0.0.4 (2021-08-20)

- First version of generic task utilities. Constants starting with task states
  and a `TaskProtocol` class which defines (some) required properties of
  `Task` objects. Import from `funcx_common.tasks`
- Add first version of `FuncxRedisConnection` and `FuncxEndpointTaskQueue`
  utilities for wrapping redis-py. Import from `funcx_common.redis`, as in
  `from funcx_common.redis import FuncxEndpointTaskQueue`
- A new extra, `redis` defines a requirement for the redis-py lib. Install with
  `funcx-common[redis]` to pull in the redis requirement. Installation
  without `reids` will result in `FuncxRedisConnection` and
  `FuncxEndpointTaskQueue` failing to initialize
- `funcx_common.redis` now provides `RedisField`, a descriptor which is backed by
  `hset` and `hget` against the owning object's `redis_client` attribute for
  presistence. Initialization of `RedisField` requires the `HasRedisFieldsMeta`
  metaclass. `HasRedisFields` may be used to apply this metaclass via
  inheritance.
- De/serialization of `RedisField` data can be defined with "serde" objects.
  `funcx_common.redis` provides: `DEFAULT_SERDE` (strings), `INT_SERDE`,
  `JSON_SERDE`, and `FuncxRedisEnumSerde` (takes an enum class as an input)

## 0.0.3 (2021-08-17)

- Bugfix: `FuncxResponseError.unpack()` correctly handles values not in the
  known response codes enum
- Add `py.typed` to package data, to publish type annotations
- Bugfix: annotate `FuncxResponseError.http_status_code` as a class var

## 0.0.2 (2021-08-17)

- Fix links to repo/homepage (including in package metadata)

## 0.0.1 (2021-08-17)

- Initial Release
