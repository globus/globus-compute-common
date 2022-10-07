### Added

- Add `queue_name` field to `RedisTask`.  This specifies the name of the AMQP
  queue where this task's result will be put or found.  If not set, this task's
  result will not be placed into an AMQP queue.
