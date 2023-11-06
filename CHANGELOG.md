# Changelog

<!-- scriv-insert-here -->

<a id='changelog-0.3.0'></a>
## 0.3.0 (2023-08-07)

### Changed

- Added metadata dict to Result message
- Added details dict to RedisTask

<a id='changelog-0.2.0'></a>
## 0.2.0 (2023-05-10)

### Fixed

- Quashed warning that would be logged when deserializing `EPStatusReport` messages
  using the `ep_status_report` alias for `global_state`

<a id='changelog-0.1.0'></a>
## 0.1.0 (2023-03-06)

### Changed

- Renamed funcx-common to globus-compute-common package

<a id='changelog-0.0.25'></a>
## 0.0.25 (2023-03-06)

### Changed

- Renamed the `ep_status_report` field of the `EPStatusReport` message to
  `global_state`

  - `global_state` has an alias of `ep_status_report` for backward compatibility

<a id='changelog-0.0.24'></a>
## 0.0.24 (2023-01-23)

### Changed

- Container information can now be conveyed directly with Task messages, not just ``container_id``

<a id='changelog-0.0.23'></a>
## 0.0.23 (2022-12-06)

### Added

- Add an exception and error code for when a serialized function exceeds our size limits.

<a id='changelog-0.0.21'></a>
## 0.0.21 (2022-12-02)

### Added

- Add new exception, `ContainerBuildForbidden`

<a id='changelog-0.0.20'></a>
## 0.0.20 (2022-11-18)

### Added

- Added error codes and classes for when submissions to the web service's `batch_run` API are too large

<a id='changelog-0.0.17'></a>
## 0.0.17 (2022-10-19)

### Added

- A `TaskTransition` message type which is used in the Result, ManagerStatusReport, and EPStatusReport to record status events.
- Execution-start and execution-end TaskState constants.
- ActorName constants to represent the various entities in the system.

<a id='changelog-0.0.16'></a>
## 0.0.16 (2022-10-11)

### Added

- Add `queue_name` field to `RedisTask`.  This specifies the name of the AMQP
  queue where this task's result will be put or found.  If not set, this task's
  result will not be placed into an AMQP queue.

## 0.0.15 (2022-07-15)

### Added

- Added a `.status_log` property to the RedisTask object.  The state log
  requires an atomic append, so this cannot be implemented as another field in
  the RedisTask hash.  Instead, it is implemented as a top-level array.

## 0.0.14 (2022-06-13)

### Changed

- `Task` messages no longer require `container_id`, in support of running tasks that don't require containers.

### Added

- An `sdk_version_sharing` module for centralizing the behavior where the SDK sends its version string to the Web Service for logging.

- A new error class has been added, `messagepack.WrongMessageTypeError`

- All `messagepack.Message` objects now support a new method,
  `assert_one_of_types`, which takes `Message` subclasses as arguments and
  raises a `WrongMessageTypeError` if `isinstance(..., message_types)` does not
  pass

## 0.0.13 (2022-05-20)

### Added

- `funcx_common.messagepack` now provides a default `MessagePacker` instance,
  created at import time. This also allows for `pack` and `unpack` methods to
  be provided as functions from the package. The following names are now
  available for import and use:

  - `funcx_common.messagepack.DEFAULT_MESSAGE_PACKER`
  - `funcx_common.messagepack.pack`
  - `funcx_common.messagepack.unpack`

- `funcx_common.messagepack.message_types.Result` now supports two new
  optional attributes: `exec_start_ms` and `exec_end_ms`, for execution timing
  info in milliseconds since epoch.

- `funcx_common.messagepack.message_types.Result` has a computed property
  `exec_duration_ms` which takes `exec_end_ms - exec_start_ms`

## 0.0.12 (2022-02-15)

### Added

- `InvalidAuthToken` and `InsufficientAuthScope` error classes were added for auth errors that occur in the web service

- Implementation of v1 of the `funcx.messagepack` protocol.
  See [the readme](src/globus_compute_common/messagepack/) for more info

- The following message types have been added to `messagepack`: `Result`,
  `TaskCancel`

  - `Result` defines an additional model for de/serializing errors:
    `funcx_common.messagepack.message_types.ResultErrorDetails`. The
    `ResultErrorDetails` object is used to wrap a string code and a user-facing
    message

  - `TaskCancel` is defined only to have the `task_id` field

### Removed

- Remove the v0 implementation of `funcx.messagepack`

- The following message types have been removed from `messagepack`:
    `Heartbeat`, `HeartbeatReq`, `ResultsAck`

### Changed

- `pydantic>=1,<2` is now required by `funcx-common`

- Messages in the `funcx.messagepack` subpackage are now pydantic models, and their
  members have changed. The `message_type` is now a  `str`, not an enum

## 0.0.11 (2022-01-04)

### Added

- A new class, `funcx_common.redis_task.RedisTask` has been added, which
  implements the `TaskProtocol` backed with `RedisField` attributes. This
  follows the pattern of existing implementations.

- `RedisTask.load` is added as a classmethod for loading tasks from Redis with
  the requirement that the task must exist in Redis

- A new enum has been added, `funcx_common.tasks.InternalTaskState`, for
  task `internal_status` values

- `funcx_common.task_storage.TaskStorage` and its child classes (`ImplicitRedisStorage` and
    `RedisS3Storage`) now support `store_payload` and `get_payload` methods.

## 0.0.10 (2021-11-30)

### Added

- A new subpackage, `funcx_common.messagepack` provides an implementation of
  serialization and deserialization of message objects meant to be compatible
  with `funcx_endpoint.executors.high_throughput.messages` in its on-the-wire
  representation of messages. Changes between the two implementations are
  noted in a README for `messagepack`.

  - `messagepack` defines protocol versions, starting with the current and
    unversioned v0, for handling changes to the protocol over time

  - only v0 is implemented, but a suggested plan for v1 of the protocol can be
    seen in the `messagepack` readme

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

## 0.0.9 (2021-11-04)

### Added

- A new TaskStorage class that is designed to abstract the storage systems for result or payload blobs
- A RedisS3Storage implementation which is ready for use for storing results.

  - This will store small results in Redis and large results in S3 using a
    configurable threshold.
  - The write to redis is implicit, assuming that task objects define `result`
      as a `RedisField`

- TaskProtocol now defines a new dict attribute: `result_reference`, which is
  written and read by the TaskStorage component. Tasks must add an
  implementation of this field to comply with the protocol.

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
-
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
