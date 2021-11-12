import json
import typing as t
import uuid

from ..common import Message, MessageType
from ..exceptions import InvalidMessagePayloadError


class EPStatusReport(Message):
    """
    Status report for an endpoint, sent from Endpoint to Forwarder.

    Includes EP-wide info such as utilization, as well as per-task status information.
    """

    message_type = MessageType.EP_STATUS_REPORT

    def __init__(
        self,
        endpoint_id: str,
        ep_status_report: t.Dict[str, t.Any],
        task_statuses: t.Dict[str, t.Any],
    ) -> None:
        self.endpoint_id = endpoint_id
        self.ep_status = ep_status_report
        self.task_statuses = task_statuses

    @property
    def endpoint_id_bytes(self) -> bytes:
        return uuid.UUID(self.endpoint_id).bytes

    def get_v0_body(self) -> bytes:
        # NOTE: it's important that this is done as a dumps(...).encode("ascii")
        # rather than the more normal "dumps(..., ensure_ascii=True)"
        # the reason is that this is the method of encoding used in `funcx-endpoint` and
        # we must be sure that
        # 1. messages written by this module can be read there
        # 2. messages written by that module can be read here
        #
        # (1) is ensured by this method of encoding in this function
        # (2) is ensured by testing that `load_v0_body` is an inverse for this method
        jsonified = json.dumps(
            [self.ep_status, self.task_statuses],
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        return self.endpoint_id_bytes + jsonified

    @classmethod
    def load_v0_body(cls, buf: bytes) -> "EPStatusReport":
        if len(buf) <= 16:
            raise InvalidMessagePayloadError("EPStatusReport body was too short")

        # this cannot fail because any 16-byte sequence can be converted to a UUID
        endpoint_id = str(uuid.UUID(bytes=buf[:16]))

        buf = buf[16:]
        jsonified = buf.decode("ascii")
        try:
            loaded_json = json.loads(jsonified)
        except ValueError as e:
            raise InvalidMessagePayloadError(
                "EPStatusReport body did not contain JSON section"
            ) from e

        if not (isinstance(loaded_json, list) and len(loaded_json) == 2):
            raise InvalidMessagePayloadError(
                "EPStatusReport json data was improperly shaped"
            )

        ep_status, task_statuses = loaded_json
        if not (isinstance(ep_status, dict) and isinstance(task_statuses, dict)):
            raise InvalidMessagePayloadError(
                "EPStatusReport inner json data was improperly shaped"
            )

        return cls(endpoint_id, ep_status, task_statuses)
