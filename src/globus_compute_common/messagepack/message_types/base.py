from __future__ import annotations

import pydantic
import typing as t

from pydantic import BaseModel

from ..exceptions import WrongMessageTypeError

MT = t.TypeVar("MT", bound=t.Type["Message"])


class Message(BaseModel):
    # pydantic inspects most data on the class itself
    # use an internal class to declare attributes of the message class which should not
    # be treated by pydantic as part of the model
    class Meta:
        message_type: t.ClassVar[str]

    @property
    def message_type(self) -> str:
        return self.Meta.message_type

    # common Config for all of our pydantic models
    class Config:
        version = [int(num) for num in pydantic.__version__.split(".")]
        major_version = version[0]
        if major_version < 2:
            # Set this flag if using Pydantic V2 to allow underscore-prefixed attrs
            # to be used rather than pydantic.PrivateAttr to declare instance variables
            # on models which are not part of the serialized data.
            #
            # See the following links:
            # - attr: https://pydantic-docs.helpmanual.io/usage/models/#private-model-attributes
            # - V2 migration: https://docs.pydantic.dev/latest/migration/#removed-in-pydantic-v2
            underscore_attrs_are_private = True

    def assert_one_of_types(self, *message_types: type[Message]) -> None:
        if not isinstance(self, message_types):
            raise WrongMessageTypeError(
                f"expected {message_types} but got {type(self)}"
            )


# a handy class decorator for assigning fields to the internal Meta class
# correctly subclasses any Meta which might be defined on a message type
def meta(**kwargs: t.Any) -> t.Callable[[MT], MT]:
    def class_decorator(cls: MT) -> MT:
        if not hasattr(cls, "Meta"):
            bases: tuple[type[t.Any], ...] = ()
        else:
            bases = (cls.Meta,)

        # this is incomprehensible magic to mypy, just type-ignore it
        cls.Meta = type("Meta", bases, {})  # type: ignore

        for k, v in kwargs.items():
            setattr(cls.Meta, k, v)

        return cls

    return class_decorator
