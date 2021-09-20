import queue
import uuid

import pytest

from funcx_common.redis import FuncxRedisPubSub
from funcx_common.tasks import TaskProtocol, TaskState
from funcx_common.testing import LOCAL_REDIS_REACHABLE


class SimpleInMemoryTask(TaskProtocol):
    def __init__(self):
        self.task_id = str(uuid.uuid1())
        self.endpoint = None
        self.status = TaskState.RECEIVED


@pytest.mark.skipif(
    not LOCAL_REDIS_REACHABLE, reason="test requires local redis reachable"
)
def test_put_and_get_single_task():
    producer = FuncxRedisPubSub("localhost")
    consumer = FuncxRedisPubSub("localhost")
    t = SimpleInMemoryTask()
    epid = str(uuid.uuid1())

    consumer.subscribe(epid)

    recipients = producer.put(epid, t)
    assert recipients == 1

    res = consumer.get()
    assert res == (epid, t.task_id)


@pytest.mark.skipif(
    not LOCAL_REDIS_REACHABLE, reason="test requires local redis reachable"
)
def test_put_and_get_single_task_deferred():
    # same as above, but do the subscribe call after pushing the task into the
    # queue
    producer = FuncxRedisPubSub("localhost")
    consumer = FuncxRedisPubSub("localhost")
    t = SimpleInMemoryTask()
    epid = str(uuid.uuid1())

    recipients = producer.put(epid, t)
    assert recipients == 0

    consumer.subscribe(epid)
    res = consumer.get()
    assert res == (epid, t.task_id)


@pytest.mark.skipif(
    not LOCAL_REDIS_REACHABLE, reason="test requires local redis reachable"
)
def test_empty_get():
    consumer = FuncxRedisPubSub("localhost")
    epid = str(uuid.uuid1())

    consumer.subscribe(epid)
    with pytest.raises(queue.Empty):
        consumer.get()


@pytest.mark.skipif(
    not LOCAL_REDIS_REACHABLE, reason="test requires local redis reachable"
)
def test_subscribed_status():
    consumer = FuncxRedisPubSub("localhost")
    epid = str(uuid.uuid1())

    assert not consumer.subscribed

    consumer.subscribe(epid)
    assert consumer.subscribed

    consumer.unsubscribe(epid)
    assert consumer.subscribed  # still subscribed
    last_messages = list(consumer.get_final_messages())
    assert last_messages == []
    assert not consumer.subscribed


@pytest.mark.skipif(
    not LOCAL_REDIS_REACHABLE, reason="test requires local redis reachable"
)
def test_unsubscribe_and_resubscribe():
    # subscribe, get a task, unsubscribe, task is not gotten, resubscribe and
    # get again

    producer = FuncxRedisPubSub("localhost")
    consumer = FuncxRedisPubSub("localhost")
    t1 = SimpleInMemoryTask()
    t2 = SimpleInMemoryTask()
    epid = str(uuid.uuid1())

    consumer.subscribe(epid)

    recipients = producer.put(epid, t1)
    assert recipients == 1

    res = consumer.get()
    assert res == (epid, t1.task_id)

    consumer.unsubscribe(epid)
    # consume the final messages
    # this ensures that there are none, but also walks through any published
    # messages and marks the consumer as no longer subscribed to the channel
    # without this, it is possible that redis has not yet processed the
    # unsubscribe -- it then would be possible for the producer.put() call
    # below to return 1
    last_messages = list(consumer.get_final_messages())
    assert last_messages == []

    recipients = producer.put(epid, t2)
    assert recipients == 0

    with pytest.raises(queue.Empty):
        consumer.get()

    consumer.subscribe(epid)
    res = consumer.get()
    assert res == (epid, t2.task_id)
