### Removed

- The following message types have been removed from `messagepack`:
    `Heartbeat`, `HeartbeatReq`, `ResultsAck`

### Added

- The following message types have been added to `messagepack`: `Result`,
  `TaskCancel`

  - `Result` defines additional classes for serializing errors:
      `funcx_common.messagepack.message_types.ResultErrorCode` and
      `funcx_common.messagepack.message_types.ResultErrorDetails`

  - `TaskCancel` is defined only to have the `task_id` field
