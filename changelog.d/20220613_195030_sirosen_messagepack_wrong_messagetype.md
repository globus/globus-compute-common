### Added

- A new error class has been added, `messagepack.WrongMessageTypeError`

- All `messagepack.Message` objects now support a new method,
  `assert_one_of_types`, which takes `Message` subclasses as arguments and
  raises a `WrongMessageTypeError` if `isinstance(..., message_types)` does not
  pass
