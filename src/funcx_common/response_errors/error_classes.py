import datetime
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


class ContainerBuildForbidden(FuncxResponseError):
    """User not entitled to use container service"""

    code = ResponseErrorCode.CONTAINER_SERVICE_NOT_PERMITTED
    http_status_code = HTTPStatusCode.FORBIDDEN

    def __init__(self) -> None:
        self.reason = "Unauthorized container service access"
        self.error_args = [""]


class EndpointAlreadyRegistered(FuncxResponseError):
    """Endpoint with specified uuid already registered by a different user"""

    code = ResponseErrorCode.ENDPOINT_ALREADY_REGISTERED
    http_status_code = HTTPStatusCode.FORBIDDEN

    def __init__(self, ep_uuid: t.Union[uuid.UUID, str]) -> None:
        ep_uuid = str(ep_uuid)
        self.error_args = [ep_uuid]
        self.reason = f"Endpoint {ep_uuid} was already registered by a different user"
        self.uuid = ep_uuid


class EndpointInUseError(FuncxResponseError):
    """Endpoint is already being used in another way.
    i.e. The UUID is already being used by another active endpoint, or
    the endpoint is already configured differently from a prior registration
    """

    code = ResponseErrorCode.RESOURCE_CONFLICT
    http_status_code = HTTPStatusCode.RESOURCE_CONFLICT

    def __init__(self, ep_uuid: t.Union[uuid.UUID, str], reason: str) -> None:
        ep_uuid = str(ep_uuid)
        self.error_args = [ep_uuid]
        self.reason = f"Endpoint {ep_uuid} is already in use: {reason}"
        self.uuid = ep_uuid


class EndpointLockedError(FuncxResponseError):
    """Endpoint with specified uuid cannot be registered until the lock expires"""

    code = ResponseErrorCode.RESOURCE_LOCKED
    http_status_code = HTTPStatusCode.RESOURCE_LOCKED

    def __init__(
        self,
        ep_uuid: t.Union[uuid.UUID, str],
        expire_ts: t.Optional[float] = None,
    ) -> None:
        ep_uuid = str(ep_uuid)
        self.error_args = [ep_uuid]
        self.reason = f"Endpoint id {ep_uuid} is temporarily locked from registration"
        if expire_ts is not None:
            expire_time = datetime.datetime.fromtimestamp(expire_ts).astimezone()
            self.reason += f" until {expire_time.isoformat()}"
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


class InvalidAuthToken(FuncxResponseError):
    """Invalid auth token sent in request"""

    code = ResponseErrorCode.INVALID_AUTH_TOKEN
    http_status_code = HTTPStatusCode.UNAUTHORIZED

    def __init__(self) -> None:
        self.error_args = []
        self.reason = "Credentials are invalid"


class InsufficientAuthScope(FuncxResponseError):
    """Invalid auth token sent in request"""

    code = ResponseErrorCode.INSUFFICIENT_AUTH_SCOPE
    http_status_code = HTTPStatusCode.FORBIDDEN

    def __init__(self) -> None:
        self.error_args = []
        self.reason = "Insufficient scope for this action"


class BatchRunTooLarge(FuncxResponseError):
    """Raised when the size of the POST body sent to the batch_run API
    exceeds our limits."""

    code = ResponseErrorCode.BATCH_RUN_TOO_LARGE
    http_status_code = HTTPStatusCode.PAYLOAD_TOO_LARGE

    def __init__(self, payload_size: int, max_size: int):
        self.error_args = [payload_size, max_size]
        self.reason = (
            "Batch submission is too large: "
            + f"{payload_size} bytes > {max_size} bytes"
        )


class TaskPayloadTooLarge(FuncxResponseError):
    """Raised when the payload of a task sent to the batch_run API
    exceeds our limits."""

    code = ResponseErrorCode.TASK_PAYLOAD_TOO_LARGE
    http_status_code = HTTPStatusCode.PAYLOAD_TOO_LARGE

    def __init__(
        self,
        task_group_id: str,
        task_id: str,
        max_size: int,
        function_code_size: int,
        arguments_size: int,
    ):
        self.error_args = [
            task_group_id,
            task_id,
            max_size,
            function_code_size,
            arguments_size,
        ]
        payload_size = function_code_size + arguments_size
        self.reason = (
            f"Payload for task {task_id} in task group {task_group_id} is "
            + f"too large: {payload_size} bytes > {max_size} bytes "
            + f"({function_code_size} bytes due to serialized function code, "
            + f"{arguments_size} bytes due to arguments)"
        )


class FunctionTooLarge(FuncxResponseError):
    """Raised when the size of a serialized function sent to the API
    exceeds our limits."""

    code = ResponseErrorCode.FUNCTION_TOO_LARGE
    http_status_code = HTTPStatusCode.PAYLOAD_TOO_LARGE

    def __init__(self, function_size: int, max_size: int) -> None:
        self.error_args = [function_size, max_size]
        self.reason = (
            f"The submitted function is {function_size} bytes, "
            f"which exceeds the maximum limit of {max_size} bytes"
        )
