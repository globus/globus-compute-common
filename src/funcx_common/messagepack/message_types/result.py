from __future__ import annotations

import enum
import typing as t
import uuid

import pydantic

from .base import Message, meta


class ResultErrorCode(enum.Enum):
    ContainerError = "ContainerError"
    ManagerLost = "ManagerLost"
    EndpointGone = "EndpointGone"
    ProvisioningError = "ProvisioningError"


class ResultErrorDetails(pydantic.BaseModel, use_enum_values=True):
    # is the error related to FuncX internals or not?
    is_system_error: bool
    # an enumerated string for the error code
    code: ResultErrorCode
    # the user is always supposed to see user_message somewhere
    user_message: str

    # special validator handles the conversion of the "code" from string values, to
    # enable us to load JSON data
    #
    # pydantic docs discuss using `use_enum_values=True` and inheriting from
    # `(str, enum.Enum)`
    # however, those solutions change the behavior of the model when serializing, and
    # neither one corrects for the issue encountered when deserializing
    # use_enum_values will take care of the serialization issue, but this "validator"
    # handles deserialization
    @pydantic.validator("code", pre=True)
    def _code_from_str(cls, v: str | ResultErrorCode) -> ResultErrorCode:
        if isinstance(v, str):
            return ResultErrorCode(v)
        return v


@meta(message_type="result")
class Result(Message):
    task_id: uuid.UUID
    data: str
    error_details: t.Optional[ResultErrorDetails]

    @property
    def is_error(self) -> bool:
        return self.error_details is not None
