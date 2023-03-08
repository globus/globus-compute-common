import typing as t
from datetime import datetime

from .redis import FLOAT_SERDE, HasRedisFieldsMeta, RedisField

try:
    import redis

    has_redis = True
except ImportError:
    has_redis = False


class RedisEndpointLock(metaclass=HasRedisFieldsMeta):
    """
    ORM-esque class to wrap access to a lock on an endpoint UUID

    Creation:
      Create a lock by instantiating this class, e.g.
      >>> RedisEndpointLock(redis_client, "e_uuid_12345", 1665605117.077466)

    Finding:
      Returns a lock dict if the lock exists for the endpoint
      >>> RedisEndpointLock.find(redis_client, "e_uuid_12345")
      This will return None if there was no lock

    Checking for lock:
      Method that returns True if there exists a lock *now* for
      the specified endpoint UUID
      >>> RedisEndpointLock.exists(redis_client, "e_uuid_12345")

    This class provides various task fields as descriptors via RedisField, and is
    responsible for de/serializing various data from/to hstore in Redis.
    """

    endpoint_id = t.cast(str, RedisField())
    lock_expiration_ts = t.cast(float, RedisField(serde=FLOAT_SERDE))

    def __init__(
        self,
        redis_client: "redis.Redis[t.Any]",
        endpoint_id: str,
        *,
        lock_timestamp: t.Optional[float] = None,
    ):
        """
        :param Redis redis_client: Redis client for properties to get/set
        :param str endpoint_id: UUID of the task, as str
        :param float lock_timestamp: The epoch timestamp when the lock ends
        """
        # non-RedisField attributes of a RedisEndpointLock
        self.hname = f"endpoint_lock_{endpoint_id}"
        self.redis_client = redis_client
        self.endpoint_id = endpoint_id
        if lock_timestamp is not None:
            now_ts = datetime.now().timestamp()
            if lock_timestamp <= now_ts:
                raise ValueError("Requested lock timestamp must be in the future")

            # This is stored as a float in the data, for our usage
            self.lock_expiration_ts = lock_timestamp
            # expire_ts is the internal reddit expiry, millisecond precision
            self.expire_ts = lock_timestamp

    @property
    def expire_ts(self) -> float:
        # TODO replace with pexpiretime() on upgrade
        # pexpiretime() should return what we need but it's apparently not
        # in the version of redis library we use?
        # Note that this is ms precision as pexpireat setter is ms
        now_ts = datetime.now().timestamp()
        return now_ts + self.redis_client.pttl(self.hname) / 1000

    @expire_ts.setter
    def expire_ts(self, expiration_ts: float) -> None:
        """Expires lock after expiration time, if not already set."""
        ttl_ms = self.redis_client.pttl(self.hname)
        if ttl_ms < 0:
            expiration_ts_ms = int(expiration_ts * 1000)
            self.redis_client.pexpireat(self.hname, expiration_ts_ms)

    def delete(self) -> None:
        """Removes this lock from Redis, not used for initial expiring case"""
        self.redis_client.delete(self.hname)

    @classmethod
    def exists(cls, redis_client: "redis.Redis[t.Any]", endpoint_id: str) -> bool:
        """Check if a given lock exists"""
        return bool(redis_client.exists(f"endpoint_lock_{endpoint_id}"))

    @classmethod
    def load(
        cls, redis_client: "redis.Redis[t.Any]", endpoint_id: str
    ) -> "RedisEndpointLock":
        """
        Returns an object lock if it exists, otherwise raises
        """
        if cls.exists(redis_client, endpoint_id):
            return cls(redis_client, endpoint_id)
        raise ValueError(f"Cannot find lock {endpoint_id}")
