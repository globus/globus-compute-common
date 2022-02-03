class InvalidMessageError(ValueError):
    """
    Message contents did not pass validation checks.

    This can be raised during unpacking OR when creating a new message.
    """


class UnrecognizedMessageTypeError(InvalidMessageError):
    """
    An error raised when packing or unpacking a message of a type unknown to the
    messagepack protocol.
    """


class InvalidMessagePayloadError(InvalidMessageError):
    """
    When attempting to unpack a message, an invalid payload was encountered.

    It was not possible to perform message construction with the payload.
    """


class UnrecognizedProtocolVersion(InvalidMessageError):
    """
    When attempting to unpack a message, found a protocol version which was not
    supported.
    """
