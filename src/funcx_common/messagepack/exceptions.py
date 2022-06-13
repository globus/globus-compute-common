class InvalidMessageError(ValueError):
    """
    Message contents did not pass validation checks.

    This can be raised during unpacking OR when creating a new message.
    """


class UnrecognizedProtocolVersion(InvalidMessageError):
    """
    When attempting to unpack a message, found a protocol version which was not
    supported.
    """


class WrongMessageTypeError(ValueError):
    """
    Raised when a message has its type asserted and the type does not match the code's
    expectations.
    """
