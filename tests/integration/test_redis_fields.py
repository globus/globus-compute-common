import pytest

from funcx_common.redis import (
    INT_SERDE,
    FuncxRedisEnumSerde,
    HasRedisFields,
    RedisField,
)
from funcx_common.tasks import TaskState
from funcx_common.testing import LOCAL_REDIS_REACHABLE

try:
    import redis

    has_redis = True
except ImportError:
    has_redis = False


REAL_REDIS_HNAMES = [
    "redis_testing_task_id_1",
]


@pytest.fixture(scope="module")
def redis_client():
    if not (LOCAL_REDIS_REACHABLE and has_redis):
        pytest.skip("test requires local redis reachable")
    client = redis.Redis("localhost", port=6379, decode_responses=True)

    for hname in REAL_REDIS_HNAMES:
        for key, _value in client.hscan_iter(hname):
            client.hdel(hname, key)

    return client


class MockRedis:
    def __init__(self):
        self.data = {}

    def hset(self, hname, key, value):
        self.data.setdefault(hname, {})
        self.data[hname][key] = value

    def hget(self, hname, key):
        self.data.setdefault(hname, {})
        return self.data[hname].get(key)


def test_redis_field_key_init():
    class MyClass(HasRedisFields):
        foo = RedisField()
        bar = RedisField()

        def __init__(self):
            self.redis_client = MockRedis()
            self.hname = "somename"

    # sanity check -- make sure we're accessing the descriptor, not its value
    assert isinstance(vars(MyClass)["foo"], RedisField)
    assert vars(MyClass)["foo"].key == "foo"
    assert vars(MyClass)["bar"].key == "bar"


def test_redis_field_setter():
    mredis = MockRedis()

    class C1(HasRedisFields):
        def __init__(self):
            self.redis_client = mredis
            self.hname = "c1"

        foo = RedisField()
        bar = RedisField(serde=INT_SERDE)

    class C2(HasRedisFields):
        def __init__(self):
            self.redis_client = mredis
            self.hname = "c2"

        foo = RedisField(serde=FuncxRedisEnumSerde(TaskState))

    c1inst = C1()
    c2inst = C2()

    c1inst.foo = "ohai"
    c1inst.bar = 3
    c2inst.foo = TaskState.WAITING_FOR_NODES

    assert mredis.data["c1"]["foo"] == "ohai"
    assert mredis.data["c1"]["bar"] == "3"
    assert mredis.data["c2"]["foo"] == "waiting-for-nodes"


def test_redis_field_getter():
    mredis = MockRedis()

    class C1(HasRedisFields):
        def __init__(self):
            self.redis_client = mredis
            self.hname = "c1"

        foo = RedisField()

    mredis.data["c1"] = {"foo": "ohai"}

    c1inst = C1()

    assert c1inst.foo == "ohai"


def test_redis_field_with_real_storage(redis_client):
    class TaskClass(HasRedisFields):
        foo = RedisField()
        state = RedisField(serde=FuncxRedisEnumSerde(TaskState))

        def __init__(self):
            self.redis_client = redis_client
            self.hname = REAL_REDIS_HNAMES[0]

    task = TaskClass()
    assert task.foo is None
    task.foo = "test data"
    assert task.foo == "test data"

    assert task.state is None
    task.state = TaskState.RUNNING
    assert task.state is TaskState.RUNNING


def test_cannot_use_redis_field_outside_of_class_structure():
    class MyClass:
        foo = RedisField()

    x = MyClass()

    with pytest.raises(TypeError):
        x.foo
