### Added

- A new class, `funcx_common.redis_task.RedisTask` has been added, which
  implements the `TaskProtocol` backed with `RedisField` attributes. This
  follows the pattern of existing implementations.
- `RedisTask.load` is added as a classmethod for loading tasks from Redis with
  the requirement that the task must exist in Redis
- A new enum has been added, `funcx_common.tasks.InternalTaskState`, for
  task `internal_status` values
