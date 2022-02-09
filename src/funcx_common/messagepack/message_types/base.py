from __future__ import annotations

import typing as t

from pydantic import BaseModel

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
