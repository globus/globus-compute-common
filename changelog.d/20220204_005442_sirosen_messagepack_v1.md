### Removed

- Remove the v0 implementation of `funcx.messagepack`

### Added

- Implementation of v1 of the `funcx.messagepack` protocol.
  See [the readme](src/funcx_common/messagepack/) for more info

### Changed

- Messages in the `funcx.messagepack` subpackage are now dataclasses, and their
  members have changed. The `message_type` field is now a classvar of type
  `str`, not an enum
