### Removed

- Remove the v0 implementation of `funcx.messagepack`

### Added

- Implementation of v1 of the `funcx.messagepack` protocol.
  See [the readme](src/funcx_common/messagepack/) for more info

### Changed

- `pydantic>=1,<2` is now required by `funcx-common`

- Messages in the `funcx.messagepack` subpackage are now pydantic models, and their
  members have changed. The `message_type` is now a  `str`, not an enum
