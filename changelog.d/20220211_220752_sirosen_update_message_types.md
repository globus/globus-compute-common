### Removed

- The following message types have been removed from `messagepack`:
    `Heartbeat`, `HeartbeatReq`, `ResultsAck`

### Added

- The following message types have been added to `messagepack`: `Result`,
  `TaskCancel`

  - `Result` defines an additional model for de/serializing errors:
    `funcx_common.messagepack.message_types.ResultErrorDetails`. The
    `ResultErrorDetails` object is used to wrap a string code, a user-facing
    message, and a bool to indicate that the error was retryable (FuncX-system
    related errors, as opposed to a code execution error)


  - `TaskCancel` is defined only to have the `task_id` field
