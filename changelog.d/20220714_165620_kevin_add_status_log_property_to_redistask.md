### Added

- Added a `.status_log` property to the RedisTask object.  The state log
  requires an atomic append, so this cannot be implemented as another field in
  the RedisTask hash.  Instead, it is implemented as a top-level array.
