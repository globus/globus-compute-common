import typing as t

from ...tasks.constants import ActorName, TaskState
from .base import Message, meta


@meta(message_type="task_transition")
class TaskTransition(Message):
    timestamp: int
    state: TaskState
    actor: ActorName

    def to_dict(self) -> t.Dict[str, t.Any]:
        return {
            "timestamp": self.timestamp,
            "state": self.state.value,
            "actor": self.actor.value,
        }
