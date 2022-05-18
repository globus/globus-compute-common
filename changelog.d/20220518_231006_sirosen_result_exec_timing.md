### Added

- `funcx_common.messagepack.message_types.Result` now supports two new
  optional attributes: `exec_start_ms` and `exec_end_ms`, for execution timing
  info in milliseconds since epoch.
- `funcx_common.messagepack.message_types.Result` has a computed property
  `exec_duration_ms` which takes `exec_end_ms - exec_start_ms`
