import functools
import typing as t

from .serde import DEFAULT_SERDE, FuncxRedisSerde

RT = t.TypeVar("RT")
_null_key = "__NULL_KEY__"


def _check_null_key(func: t.Callable[..., RT]) -> t.Callable[..., RT]:
    @functools.wraps(func)
    def wrapper(self: "RedisField", *args: t.Any, **kwargs: t.Any) -> RT:
        if self.key == "__NULL_KEY__":
            raise TypeError(
                "Cannot use RedisField outside of a class with "
                "HasRedisFieldsMeta. Inherit from HasRedisFields or set "
                "metaclass to HasRedisFieldsMeta."
            )
        return func(self, *args, **kwargs)

    return wrapper


class RedisField:
    """
    Descriptor class that stores data in redis.

    Uses owning class's redis client in `owner.redis_client` to connect, and uses
    owner's hname in `owner.hname` to uniquely identify the keys.

    Fields can be serialized and deserialized by setting a FuncxRedisSerde.
    """

    # TODO: have a cache and TTL on the properties so that we aren't making so many
    #       redis gets?
    def __init__(self, serde: FuncxRedisSerde = DEFAULT_SERDE) -> None:
        self.serde = serde
        self.key: str = _null_key  # will be overwritten

    @_check_null_key
    def __get__(self, owner: t.Any, ownertype: t.Type) -> t.Any:
        value = owner.redis_client.hget(owner.hname, self.key)
        return None if value is None else self.serde.deserialize(value)

    @_check_null_key
    def __set__(self, owner: t.Any, val: t.Any) -> None:
        owner.redis_client.hset(owner.hname, self.key, self.serde.serialize(val))


class HasRedisFieldsMeta(type):
    """
    This metaclass should be used by any class which has RedisFields included.
    It is also provided via the HasRedisFields class for use in simple
    inheritance, for convenience.

    This inspects all class attributes and sets the keys on RedisField
    attributes to be the same as their attribute name.
    """

    # don't type check __new__ -- metaclasses are hard for mypy
    def __new__(mcls, classname, bases, class_attrs):  # type: ignore
        for attrname, value in class_attrs.items():
            if isinstance(value, RedisField):
                value.key = attrname
        return super().__new__(mcls, classname, bases, class_attrs)


class HasRedisFields(metaclass=HasRedisFieldsMeta):
    pass
