import typing as t
import uuid

from .base import Message, meta


@meta(message_type="containerimage")
class ContainerImage(Message):
    image_type: str  # e.g., (as currently envisioned), 'docker', 'singularity'
    location: str  # location or name required to pull the image (e.g., python:3.10)
    created_at: int
    modified_at: int
    build_status: t.Optional[str]
    build_stderr: t.Optional[str]


@meta(message_type="container")
class Container(Message):
    container_id: uuid.UUID
    name: str
    images: t.List[ContainerImage]
