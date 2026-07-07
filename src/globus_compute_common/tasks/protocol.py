import typing as t

from .constants import TaskState


class TaskProtocol(t.Protocol):
    task_id: str
    endpoint: t.Optional[str]
    status: TaskState
    result: t.Optional[str]
    result_reference: t.Optional[t.Dict[str, t.Any]]
    payload: t.Optional[str]
    payload_reference: t.Optional[t.Dict[str, t.Any]]
