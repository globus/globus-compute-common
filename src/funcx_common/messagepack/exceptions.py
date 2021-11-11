class UnrecognizedMessageTypeError(ValueError):
    """
    An error raised when packing or unpacking a message of a type unknown to the
    messagepack protocol.
    """
