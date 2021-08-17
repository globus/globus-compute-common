from .constants import HTTPStatusCode, ResponseErrorCode
from .error_base import FuncxResponseError


class UserUnauthenticated(FuncxResponseError):
    """User unauthenticated. This differs from UserNotFound in that it has a 401 HTTP
    status code, whereas UserNotFound has a 404 status code. This error should be used
    when the user's request failed because the user was unauthenticated, regardless of
    whether the request itself required looking up user info.
    """

    code = ResponseErrorCode.USER_UNAUTHENTICATED
    # this HTTP status code is called unauthorized but really means "unauthenticated"
    # according to the spec
    http_status_code = HTTPStatusCode.UNAUTHORIZED

    def __init__(self):
        self.error_args = []
        self.reason = (
            "Could not find user. You must be logged in to perform this function."
        )


class UserNotFound(FuncxResponseError):
    """User not found exception. This error should only be used when the server must
    look up a user in order to fulfill the user's request body. If the request only
    fails because the user is unauthenticated, UserUnauthenticated should be used
    instead.
    """

    code = ResponseErrorCode.USER_NOT_FOUND
    http_status_code = HTTPStatusCode.NOT_FOUND

    def __init__(self, reason):
        reason = str(reason)
        self.error_args = [reason]
        self.reason = reason


class FunctionNotFound(FuncxResponseError):
    """Function could not be resolved from the database"""

    code = ResponseErrorCode.FUNCTION_NOT_FOUND
    http_status_code = HTTPStatusCode.NOT_FOUND

    def __init__(self, uuid):
        self.error_args = [uuid]
        self.reason = f"Function {uuid} could not be resolved"
        self.uuid = uuid


class EndpointNotFound(FuncxResponseError):
    """Endpoint could not be resolved from the database"""

    code = ResponseErrorCode.ENDPOINT_NOT_FOUND
    http_status_code = HTTPStatusCode.NOT_FOUND

    def __init__(self, uuid):
        self.error_args = [uuid]
        self.reason = f"Endpoint {uuid} could not be resolved"
        self.uuid = uuid


class ContainerNotFound(FuncxResponseError):
    """Container could not be resolved"""

    code = ResponseErrorCode.CONTAINER_NOT_FOUND
    http_status_code = HTTPStatusCode.NOT_FOUND

    def __init__(self, uuid):
        self.error_args = [uuid]
        self.reason = f"Container {uuid} not found"
        self.uuid = uuid


class TaskNotFound(FuncxResponseError):
    """Task could not be resolved"""

    code = ResponseErrorCode.TASK_NOT_FOUND
    http_status_code = HTTPStatusCode.NOT_FOUND

    def __init__(self, uuid):
        self.error_args = [uuid]
        self.reason = f"Task {uuid} not found"
        self.uuid = uuid


class AuthGroupNotFound(FuncxResponseError):
    """AuthGroup could not be resolved"""

    code = ResponseErrorCode.AUTH_GROUP_NOT_FOUND
    http_status_code = HTTPStatusCode.NOT_FOUND

    def __init__(self, uuid):
        self.error_args = [uuid]
        self.reason = f"AuthGroup {uuid} not found"
        self.uuid = uuid


class FunctionAccessForbidden(FuncxResponseError):
    """Unauthorized function access by user"""

    code = ResponseErrorCode.FUNCTION_ACCESS_FORBIDDEN
    http_status_code = HTTPStatusCode.FORBIDDEN

    def __init__(self, uuid):
        self.error_args = [uuid]
        self.reason = f"Unauthorized access to function {uuid}"
        self.uuid = uuid


class EndpointAccessForbidden(FuncxResponseError):
    """Unauthorized endpoint access by user"""

    code = ResponseErrorCode.ENDPOINT_ACCESS_FORBIDDEN
    http_status_code = HTTPStatusCode.FORBIDDEN

    def __init__(self, uuid):
        self.error_args = [uuid]
        self.reason = f"Unauthorized access to endpoint {uuid}"
        self.uuid = uuid


class FunctionNotPermitted(FuncxResponseError):
    """Function not permitted on endpoint"""

    code = ResponseErrorCode.FUNCTION_NOT_PERMITTED
    http_status_code = HTTPStatusCode.FORBIDDEN

    def __init__(self, function_uuid, endpoint_uuid):
        self.error_args = [function_uuid, endpoint_uuid]
        self.reason = (
            f"Function {function_uuid} not permitted on endpoint {endpoint_uuid}"
        )
        self.function_uuid = function_uuid
        self.endpoint_uuid = endpoint_uuid


class EndpointAlreadyRegistered(FuncxResponseError):
    """Endpoint with specified uuid already registered by a different user"""

    code = ResponseErrorCode.ENDPOINT_ALREADY_REGISTERED
    http_status_code = HTTPStatusCode.BAD_REQUEST

    def __init__(self, uuid):
        self.error_args = [uuid]
        self.reason = f"Endpoint {uuid} was already registered by a different user"
        self.uuid = uuid


class ForwarderRegistrationError(FuncxResponseError):
    """Registering the endpoint with the forwarder has failed"""

    code = ResponseErrorCode.FORWARDER_REGISTRATION_ERROR
    http_status_code = HTTPStatusCode.BAD_GATEWAY

    def __init__(self, error_reason):
        error_reason = str(error_reason)
        self.error_args = [error_reason]
        self.reason = f"Endpoint registration with forwarder failed - {error_reason}"


class ForwarderContactError(FuncxResponseError):
    """Contacting the forwarder failed"""

    code = ResponseErrorCode.FORWARDER_CONTACT_ERROR
    http_status_code = HTTPStatusCode.BAD_GATEWAY

    def __init__(self, error_reason):
        error_reason = str(error_reason)
        self.error_args = [error_reason]
        self.reason = f"Contacting forwarder failed with {error_reason}"


class EndpointStatsError(FuncxResponseError):
    """Error while retrieving endpoint stats"""

    code = ResponseErrorCode.ENDPOINT_STATS_ERROR
    http_status_code = HTTPStatusCode.INTERNAL_SERVER_ERROR

    def __init__(self, endpoint_uuid, error_reason):
        error_reason = str(error_reason)
        self.error_args = [endpoint_uuid, error_reason]
        self.reason = (
            f"Unable to retrieve stats for endpoint: {endpoint_uuid}. {error_reason}"
        )


class LivenessStatsError(FuncxResponseError):
    """Error while retrieving endpoint stats"""

    code = ResponseErrorCode.LIVENESS_STATS_ERROR
    http_status_code = HTTPStatusCode.BAD_GATEWAY

    def __init__(self, http_status_code):
        self.error_args = [http_status_code]
        self.reason = "Forwarder did not respond with liveness stats"


class RequestKeyError(FuncxResponseError):
    """User request JSON KeyError exception"""

    code = ResponseErrorCode.REQUEST_KEY_ERROR
    http_status_code = HTTPStatusCode.BAD_REQUEST

    def __init__(self, key_error_reason):
        key_error_reason = str(key_error_reason)
        self.error_args = [key_error_reason]
        self.reason = f"Missing key in JSON request - {key_error_reason}"


class RequestMalformed(FuncxResponseError):
    """User request malformed"""

    code = ResponseErrorCode.REQUEST_MALFORMED
    http_status_code = HTTPStatusCode.BAD_REQUEST

    def __init__(self, malformed_reason):
        malformed_reason = str(malformed_reason)
        self.error_args = [malformed_reason]
        self.reason = (
            f"Request Malformed. Missing critical information: {malformed_reason}"
        )


class InternalError(FuncxResponseError):
    """Internal server error"""

    code = ResponseErrorCode.INTERNAL_ERROR
    http_status_code = HTTPStatusCode.INTERNAL_SERVER_ERROR

    def __init__(self, error_reason):
        error_reason = str(error_reason)
        self.error_args = [error_reason]
        self.reason = f"Internal server error: {error_reason}"


class EndpointOutdated(FuncxResponseError):
    """Internal server error"""

    code = ResponseErrorCode.ENDPOINT_OUTDATED
    http_status_code = HTTPStatusCode.BAD_REQUEST

    def __init__(self, min_ep_version):
        self.error_args = [min_ep_version]
        self.reason = (
            "Endpoint is out of date. "
            f"Minimum supported endpoint version is {min_ep_version}"
        )


class TaskGroupNotFound(FuncxResponseError):
    """Task Group was not found in redis"""

    code = ResponseErrorCode.TASK_GROUP_NOT_FOUND
    http_status_code = HTTPStatusCode.NOT_FOUND

    def __init__(self, uuid):
        self.error_args = [uuid]
        self.reason = f"Task Group {uuid} could not be resolved"
        self.uuid = uuid


class TaskGroupAccessForbidden(FuncxResponseError):
    """Unauthorized Task Group access by user"""

    code = ResponseErrorCode.TASK_GROUP_ACCESS_FORBIDDEN
    http_status_code = HTTPStatusCode.FORBIDDEN

    def __init__(self, uuid):
        self.error_args = [uuid]
        self.reason = f"Unauthorized access to Task Group {uuid}"
        self.uuid = uuid


class InvalidUUID(FuncxResponseError):
    """Invalid UUID provided by user"""

    code = ResponseErrorCode.INVALID_UUID
    http_status_code = HTTPStatusCode.BAD_REQUEST

    def __init__(self, reason):
        reason = str(reason)
        self.error_args = [reason]
        self.reason = reason
