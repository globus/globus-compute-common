import typing as t
import uuid

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

    def __init__(self) -> None:
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

    def __init__(self, reason: str) -> None:
        self.error_args = [reason]
        self.reason = reason


class FunctionNotFound(FuncxResponseError):
    """Function could not be resolved from the database"""

    code = ResponseErrorCode.FUNCTION_NOT_FOUND
    http_status_code = HTTPStatusCode.NOT_FOUND

    def __init__(self, func_uuid: t.Union[uuid.UUID, str]) -> None:
        func_uuid = str(func_uuid)
        self.error_args = [func_uuid]
        self.reason = f"Function {func_uuid} could not be resolved"
        self.uuid = func_uuid


class EndpointNotFound(FuncxResponseError):
    """Endpoint could not be resolved from the database"""

    code = ResponseErrorCode.ENDPOINT_NOT_FOUND
    http_status_code = HTTPStatusCode.NOT_FOUND

    def __init__(self, ep_uuid: t.Union[uuid.UUID, str]) -> None:
        ep_uuid = str(ep_uuid)
        self.error_args = [ep_uuid]
        self.reason = f"Endpoint {ep_uuid} could not be resolved"
        self.uuid = ep_uuid


class ContainerNotFound(FuncxResponseError):
    """Container could not be resolved"""

    code = ResponseErrorCode.CONTAINER_NOT_FOUND
    http_status_code = HTTPStatusCode.NOT_FOUND

    def __init__(self, container_uuid: t.Union[uuid.UUID, str]) -> None:
        container_uuid = str(container_uuid)
        self.error_args = [container_uuid]
        self.reason = f"Container {container_uuid} not found"
        self.uuid = container_uuid


class TaskNotFound(FuncxResponseError):
    """Task could not be resolved"""

    code = ResponseErrorCode.TASK_NOT_FOUND
    http_status_code = HTTPStatusCode.NOT_FOUND

    def __init__(self, task_uuid: t.Union[uuid.UUID, str]) -> None:
        task_uuid = str(task_uuid)
        self.error_args = [task_uuid]
        self.reason = f"Task {task_uuid} not found"
        self.uuid = task_uuid


class AuthGroupNotFound(FuncxResponseError):
    """AuthGroup could not be resolved"""

    code = ResponseErrorCode.AUTH_GROUP_NOT_FOUND
    http_status_code = HTTPStatusCode.NOT_FOUND

    def __init__(self, group_uuid: t.Union[uuid.UUID, str]) -> None:
        group_uuid = str(group_uuid)
        self.error_args = [group_uuid]
        self.reason = f"AuthGroup {group_uuid} not found"
        self.uuid = group_uuid


class FunctionAccessForbidden(FuncxResponseError):
    """Unauthorized function access by user"""

    code = ResponseErrorCode.FUNCTION_ACCESS_FORBIDDEN
    http_status_code = HTTPStatusCode.FORBIDDEN

    def __init__(self, func_uuid: t.Union[uuid.UUID, str]) -> None:
        func_uuid = str(func_uuid)
        self.error_args = [func_uuid]
        self.reason = f"Unauthorized access to function {func_uuid}"
        self.uuid = func_uuid


class EndpointAccessForbidden(FuncxResponseError):
    """Unauthorized endpoint access by user"""

    code = ResponseErrorCode.ENDPOINT_ACCESS_FORBIDDEN
    http_status_code = HTTPStatusCode.FORBIDDEN

    def __init__(self, ep_uuid: t.Union[uuid.UUID, str]) -> None:
        ep_uuid = str(ep_uuid)
        self.error_args = [ep_uuid]
        self.reason = f"Unauthorized access to endpoint {ep_uuid}"
        self.uuid = ep_uuid


class FunctionNotPermitted(FuncxResponseError):
    """Function not permitted on endpoint"""

    code = ResponseErrorCode.FUNCTION_NOT_PERMITTED
    http_status_code = HTTPStatusCode.FORBIDDEN

    def __init__(
        self,
        function_uuid: t.Union[uuid.UUID, str],
        endpoint_uuid: t.Union[uuid.UUID, str],
    ) -> None:
        function_uuid, endpoint_uuid = str(function_uuid), str(endpoint_uuid)
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

    def __init__(self, ep_uuid: t.Union[uuid.UUID, str]) -> None:
        ep_uuid = str(ep_uuid)
        self.error_args = [ep_uuid]
        self.reason = f"Endpoint {ep_uuid} was already registered by a different user"
        self.uuid = ep_uuid


class ForwarderRegistrationError(FuncxResponseError):
    """Registering the endpoint with the forwarder has failed"""

    code = ResponseErrorCode.FORWARDER_REGISTRATION_ERROR
    http_status_code = HTTPStatusCode.BAD_GATEWAY

    def __init__(self, error_reason: str) -> None:
        self.error_args = [error_reason]
        self.reason = f"Endpoint registration with forwarder failed - {error_reason}"


class ForwarderContactError(FuncxResponseError):
    """Contacting the forwarder failed"""

    code = ResponseErrorCode.FORWARDER_CONTACT_ERROR
    http_status_code = HTTPStatusCode.BAD_GATEWAY

    def __init__(self, error_reason: str) -> None:
        self.error_args = [error_reason]
        self.reason = f"Contacting forwarder failed with {error_reason}"


class EndpointStatsError(FuncxResponseError):
    """Error while retrieving endpoint stats"""

    code = ResponseErrorCode.ENDPOINT_STATS_ERROR
    http_status_code = HTTPStatusCode.INTERNAL_SERVER_ERROR

    def __init__(
        self, endpoint_uuid: t.Union[uuid.UUID, str], error_reason: str
    ) -> None:
        endpoint_uuid = str(endpoint_uuid)
        self.error_args = [endpoint_uuid, error_reason]
        self.reason = (
            f"Unable to retrieve stats for endpoint: {endpoint_uuid}. {error_reason}"
        )


class LivenessStatsError(FuncxResponseError):
    """Error while retrieving endpoint stats"""

    code = ResponseErrorCode.LIVENESS_STATS_ERROR
    http_status_code = HTTPStatusCode.BAD_GATEWAY

    def __init__(self, http_status_code: t.Union[int, str]) -> None:
        http_status_code = int(http_status_code)
        self.error_args = [http_status_code]
        self.reason = "Forwarder did not respond with liveness stats"


class RequestKeyError(FuncxResponseError):
    """User request JSON KeyError exception"""

    code = ResponseErrorCode.REQUEST_KEY_ERROR
    http_status_code = HTTPStatusCode.BAD_REQUEST

    def __init__(self, key_error_reason: str) -> None:
        self.error_args = [key_error_reason]
        self.reason = f"Missing key in JSON request - {key_error_reason}"


class RequestMalformed(FuncxResponseError):
    """User request malformed"""

    code = ResponseErrorCode.REQUEST_MALFORMED
    http_status_code = HTTPStatusCode.BAD_REQUEST

    def __init__(self, malformed_reason: str) -> None:
        self.error_args = [malformed_reason]
        self.reason = (
            f"Request Malformed. Missing critical information: {malformed_reason}"
        )


class InternalError(FuncxResponseError):
    """Internal server error"""

    code = ResponseErrorCode.INTERNAL_ERROR
    http_status_code = HTTPStatusCode.INTERNAL_SERVER_ERROR

    def __init__(self, error_reason: str) -> None:
        self.error_args = [error_reason]
        self.reason = f"Internal server error: {error_reason}"


class EndpointOutdated(FuncxResponseError):
    """Internal server error"""

    code = ResponseErrorCode.ENDPOINT_OUTDATED
    http_status_code = HTTPStatusCode.BAD_REQUEST

    def __init__(self, min_ep_version: str) -> None:
        self.error_args = [min_ep_version]
        self.reason = (
            "Endpoint is out of date. "
            f"Minimum supported endpoint version is {min_ep_version}"
        )


class TaskGroupNotFound(FuncxResponseError):
    """Task Group was not found in redis"""

    code = ResponseErrorCode.TASK_GROUP_NOT_FOUND
    http_status_code = HTTPStatusCode.NOT_FOUND

    def __init__(self, task_uuid: t.Union[uuid.UUID, str]) -> None:
        task_uuid = str(task_uuid)
        self.error_args = [task_uuid]
        self.reason = f"Task Group {task_uuid} could not be resolved"
        self.uuid = task_uuid


class TaskGroupAccessForbidden(FuncxResponseError):
    """Unauthorized Task Group access by user"""

    code = ResponseErrorCode.TASK_GROUP_ACCESS_FORBIDDEN
    http_status_code = HTTPStatusCode.FORBIDDEN

    def __init__(self, task_uuid: t.Union[uuid.UUID, str]) -> None:
        task_uuid = str(task_uuid)
        self.error_args = [task_uuid]
        self.reason = f"Unauthorized access to Task Group {task_uuid}"
        self.uuid = task_uuid


class InvalidUUID(FuncxResponseError):
    """Invalid UUID provided by user"""

    code = ResponseErrorCode.INVALID_UUID
    http_status_code = HTTPStatusCode.BAD_REQUEST

    def __init__(self, reason: str) -> None:
        self.error_args = [reason]
        self.reason = reason
