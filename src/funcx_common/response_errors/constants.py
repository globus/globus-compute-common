from enum import IntEnum


# IMPORTANT: new error codes can be added, but existing error codes must not be changed
# once published.
# changing existing error codes will cause problems with users that have older versions
class ResponseErrorCode(IntEnum):
    UNKNOWN_ERROR = 0
    USER_UNAUTHENTICATED = 1
    USER_NOT_FOUND = 2
    FUNCTION_NOT_FOUND = 3
    ENDPOINT_NOT_FOUND = 4
    CONTAINER_NOT_FOUND = 5
    TASK_NOT_FOUND = 6
    AUTH_GROUP_NOT_FOUND = 7
    FUNCTION_ACCESS_FORBIDDEN = 8
    ENDPOINT_ACCESS_FORBIDDEN = 9
    FUNCTION_NOT_PERMITTED = 10
    ENDPOINT_ALREADY_REGISTERED = 11
    FORWARDER_REGISTRATION_ERROR = 12
    FORWARDER_CONTACT_ERROR = 13
    ENDPOINT_STATS_ERROR = 14
    LIVENESS_STATS_ERROR = 15
    REQUEST_KEY_ERROR = 16
    REQUEST_MALFORMED = 17
    INTERNAL_ERROR = 18
    ENDPOINT_OUTDATED = 19
    TASK_GROUP_NOT_FOUND = 20
    TASK_GROUP_ACCESS_FORBIDDEN = 21
    INVALID_UUID = 22


# a collection of the HTTP status error codes that the service would make use of
class HTTPStatusCode(IntEnum):
    BAD_REQUEST = 400
    # semantically this response means "unauthenticated", according to the spec
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    REQUEST_TIMEOUT = 408
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
