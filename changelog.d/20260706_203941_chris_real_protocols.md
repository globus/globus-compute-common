### Changed

- Converted `TaskProtocol` to a true `typing.Protocol` and updated task
  implementations to rely on structural typing instead of inheriting
  from a class which was a protocol in name only.
