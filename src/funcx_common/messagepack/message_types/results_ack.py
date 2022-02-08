from __future__ import annotations

import uuid
from dataclasses import dataclass

from ..common import Message


@dataclass
class ResultsAck(Message):
    message_type = "results_ack"
    task_id: uuid.UUID
