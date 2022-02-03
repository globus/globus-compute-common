from __future__ import annotations

import uuid
from dataclasses import dataclass

from ..common import Message


@dataclass
class Task(Message):
    message_type = "task"
    task_id: str | uuid.UUID
    container_id: str | uuid.UUID
