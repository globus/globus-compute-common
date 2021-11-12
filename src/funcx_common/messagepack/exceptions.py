class UnrecognizedMessageTypeError(ValueError):
    """
    An error raised when packing or unpacking a message of a type unknown to the
    messagepack protocol.
    """


class InvalidMessagePayloadError(ValueError):
    """
    When attempting to unpack a message, an invalid payload was encountered.
    """
