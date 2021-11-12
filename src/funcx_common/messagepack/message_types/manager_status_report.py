import json
import typing as t

from ..common import Message, MessageType
from ..exceptions import InvalidMessageError, InvalidMessagePayloadError


class ManagerStatusReport(Message):
    """
    Status report sent from the Manager to the Endpoint, which mostly just amounts to
    saying which tasks are now RUNNING.
    """

    message_type = MessageType.MANAGER_STATUS_REPORT

    def __init__(self, task_statuses: t.Dict[str, t.Any], container_switch_count: int):
        if not isinstance(task_statuses, dict):
            raise InvalidMessageError(
                "EPStatusReport inner json data was improperly shaped"
            )

        self.task_statuses = task_statuses
        self.container_switch_count = container_switch_count

    def get_v0_body(self) -> bytes:
        # NOTE: it's important that this is done as a dumps(...).encode("ascii")
        # for a full explanation, see the similar note on EPStatusReport
        jsonified = json.dumps(
            self.task_statuses,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        # yeah, the int is being written as 10 bytes
        # this is a strict "for compatibility" thing, and exemplifies why this is all
        # awful and we need to switch to a well-defined protocol
        return self.container_switch_count.to_bytes(10, "little") + jsonified

    @classmethod
    def load_v0_body(cls, buf: bytes) -> "ManagerStatusReport":
        if len(buf) <= 10:
            raise InvalidMessagePayloadError("ManagerStatusReport body was too short")

        container_switch_count = int.from_bytes(buf[:10], "little")

        buf = buf[10:]
        jsonified = buf.decode("ascii")
        try:
            task_statuses = json.loads(jsonified)
        except ValueError as e:
            raise InvalidMessagePayloadError(
                "ManagerStatusReport body failed to load as JSON"
            ) from e
        return cls(task_statuses, container_switch_count)
