import uuid

from funcx_common.task_storage import (
    ChainedTaskStorage,
    MemoryTaskStorage,
    NullTaskStorage,
    ThresholdedMemoryTaskStorage,
)
from funcx_common.tasks import TaskProtocol, TaskState


class SimpleInMemoryTask(TaskProtocol):
    def __init__(self):
        self.task_id = str(uuid.uuid1())
        self.endpoint = None
        self.status = TaskState.RECEIVED


def test_memory_storage_simple():
    memstore = MemoryTaskStorage()
    result = "foo result"
    task = SimpleInMemoryTask()

    b = memstore.store_result(task, result)
    assert b is True
    assert memstore.get_result(task) == result


def test_chained_storage_first_success():
    memstore1 = MemoryTaskStorage()
    memstore2 = MemoryTaskStorage()

    chain = ChainedTaskStorage(memstore1, memstore2)

    result = "foo result"
    task = SimpleInMemoryTask()

    b = chain.store_result(task, result)
    assert b is True
    assert memstore2.get_result(task) is None
    assert memstore1.get_result(task) == result
    assert chain.get_result(task) == result


def test_thresholded_storage_limit():
    store = ThresholdedMemoryTaskStorage(result_limit_chars=10)

    result = "result"
    task = SimpleInMemoryTask()

    b = store.store_result(task, result)
    assert b is True
    assert store.get_result(task) == result

    result2 = "result too long for char limit"
    task2 = SimpleInMemoryTask()

    b = store.store_result(task2, result2)
    assert b is False
    assert store.get_result(task2) is None


def test_chained_with_threshold():
    memstore1 = ThresholdedMemoryTaskStorage(result_limit_chars=3)
    memstore2 = MemoryTaskStorage()

    chain = ChainedTaskStorage(memstore1, memstore2)

    result = "foo result"
    task = SimpleInMemoryTask()

    b = chain.store_result(task, result)
    assert b is True
    assert memstore1.get_result(task) is None
    assert memstore2.get_result(task) == result
    assert chain.get_result(task) == result


def test_null_storage():
    store = NullTaskStorage()

    result = "result"
    task = SimpleInMemoryTask()

    b = store.store_result(task, result)
    assert b is False
    assert store.get_result(task) is None


def test_failing_chain_storage():
    store1 = NullTaskStorage()
    store2 = NullTaskStorage()

    chain = ChainedTaskStorage(store1, store2)

    result = "result"
    task = SimpleInMemoryTask()

    b = chain.store_result(task, result)
    assert b is False
    assert chain.get_result(task) is None
