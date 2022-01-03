import typing as t

from .redis import (
    INT_SERDE,
    JSON_SERDE,
    FuncxRedisEnumSerde,
    HasRedisFieldsMeta,
    RedisField,
)
from .tasks import InternalTaskState, TaskProtocol, TaskState

try:
    import redis

    has_redis = True
except ImportError:
    has_redis = False


class RedisTask(TaskProtocol, metaclass=HasRedisFieldsMeta):
    """
    ORM-esque class to wrap access to properties of tasks.

    Creation:
      Create a new task by instantiating this class, e.g.
      >>> RedisTask(redis_client, "foo_id")

    Loading:
      Read a task from storage using the `load()` classmethod, e.g.
      >>> RedisTask.load(redis_client, "foo_id")

    Creation and Loading will each check `RedisTask.exists` when invoked. If the task_id
    already exists on creation, or does not exist on load, a ValueError will be raised.
    For example:
      >>> RedisTask.load(redis_client, "foo_id")
      Traceback (most recent call last):
        ...
      ValueError: Cannot load task foo_id: does not exist
      >>> RedisTask(redis_client, "foo_id")  # ok
      >>> RedisTask(redis_client, "foo_id")
      Traceback (most recent call last):
        ...
      ValueError: Conflict. Cannot create task foo_id: already exists

    This class provides various task fields as descriptors via RedisField, and is
    responsible for de/serializing various data from/to hstore in Redis.

    There are several elements of this pattern of use which need to be fixed. It is
    important to be aware of the following:
    - there is currently no use of Redis transactions, so nothing is atomic
    - Each time a field descriptor is accessed, it is read, returned, and discarded.
      Reading a field multiple times, even in a single python statement, is vulnerable
      to data races
    - no field requirements or validity are enforced -- reading a field can raise an
      error if bad data were written to Redis
    - each field is read individually, which can be inefficient and inconsistent (vs
      getall or setall semantics)
    """

    # 2 weeks in seconds
    DEFAULT_TTL: t.ClassVar[int] = 1209600

    # required fields
    # TODO: when `required=True` is supported in `RedisField`, set it for all of these
    status = t.cast(TaskState, RedisField(serde=FuncxRedisEnumSerde(TaskState)))
    internal_status = t.cast(
        InternalTaskState, RedisField(serde=FuncxRedisEnumSerde(InternalTaskState))
    )
    user_id = t.cast(int, RedisField(serde=INT_SERDE))
    function_id = t.cast(str, RedisField())
    container = t.cast(str, RedisField())
    task_group_id = t.cast(str, RedisField())
    # end required fields

    endpoint = t.cast(t.Optional[str], RedisField())

    # FIXME: `payload` is a string which is currently being round-tripped through the
    # JSON_SERDE. However, we cannot remove the use of the serde until we are prepared
    # to handle the potential resulting errors. (Namely, that loading an old payload
    # would break)
    #
    # consider:
    #   >>> json.dumps("a")
    #   '"a"'
    #
    # therefore, we need to at least try `json.loads` on the payload (or do a breaking
    # change)
    #
    # alternatively, once `payload_reference` is populated on all tasks, we can use it
    # to include a bool flag for how the field should be deserialized. This would
    # require that the serde object itself have access to the payload_reference
    payload = t.cast(t.Optional[str], RedisField(serde=JSON_SERDE))
    payload_reference = t.cast(
        t.Optional[t.Dict[str, t.Any]], RedisField(serde=JSON_SERDE)
    )
    result = t.cast(t.Optional[str], RedisField())
    result_reference = t.cast(
        t.Optional[t.Dict[str, t.Any]], RedisField(serde=JSON_SERDE)
    )
    exception = t.cast(t.Optional[str], RedisField())
    completion_time = t.cast(t.Optional[str], RedisField())

    def __init__(
        self,
        redis_client: "redis.Redis[t.Any]",
        task_id: str,
        *,
        user_id: t.Optional[int] = None,
        function_id: t.Optional[str] = None,
        container: t.Optional[str] = None,
        payload: t.Optional[str] = None,
        payload_reference: t.Optional[t.Dict[str, t.Any]] = None,
        task_group_id: t.Optional[str] = None,
    ):
        """
        If optional values are passed, then they will be written.

        Otherwise, they will fetched from any existing task entry.
        :param redis_client: Redis client for properties to get/set
        :param task_id: UUID of the task, as str
        :param user_id: ID of user to whom this task belongs
        :param function_id: UUID of the function for this task, as str
        :param container: UUID of container in which to run, as str
        :param payload: serialized function + input data
        :param task_group_id: UUID of task group that this task belongs to
        """
        # non-RedisField attributes of a RedisTask
        self.hname = f"task_{task_id}"
        self.redis_client = redis_client
        self.task_id = task_id

        # TODO: reject `RedisTask()` if the task_id already exists:
        #   if RedisTask.exists(redis_client, task_id): raise ...

        # if required attributes are not yet set, initialize them to their defaults
        if self.status is None:
            self.status = TaskState.WAITING_FOR_EP  # type: ignore[unreachable]
        if self.internal_status is None:
            self.internal_status = (  # type: ignore[unreachable]
                InternalTaskState.INCOMPLETE
            )

        # remaining RedisField attributes
        if user_id is not None:
            self.user_id = user_id
        if function_id is not None:
            self.function_id = function_id
        if container is not None:
            self.container = container
        if payload is not None:
            self.payload = payload
        if payload_reference is not None:
            self.payload_reference = payload_reference
        if task_group_id is not None:
            self.task_group_id = task_group_id

        self.ttl = self.DEFAULT_TTL

    @property
    def ttl(self) -> int:
        return self.redis_client.ttl(self.hname)

    @ttl.setter
    def ttl(self, expiration: int) -> None:
        """Expires task after expiration time, if not already set."""
        ttl_val = self.redis_client.ttl(self.hname)
        if ttl_val < 0 or expiration < ttl_val:
            # expire was not already set
            self.redis_client.expire(self.hname, expiration)

    def delete(self) -> None:
        """Removes this task from Redis, to be used after the result is gotten"""
        self.redis_client.delete(self.hname)

    @classmethod
    def exists(cls, redis_client: "redis.Redis[t.Any]", task_id: str) -> bool:
        """Check if a given task_id exists in Redis"""
        return bool(redis_client.exists(f"task_{task_id}"))

    @classmethod
    def load(cls, redis_client: "redis.Redis[t.Any]", task_id: str) -> "RedisTask":
        """
        Load a task from storage. Raises a ValueError if the task is not found.
        """
        # TODO: This has a race condition. Encapsulate it in a transaction.
        if not cls.exists(redis_client, task_id):
            raise ValueError(f"Cannot load task {task_id}: does not exist")
        return cls(redis_client, task_id)
