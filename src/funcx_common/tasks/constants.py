import enum


# subclass from str so that the enum can be JSON-encoded without adjustment
class TaskState(str, enum.Enum):
    RECEIVED = "received"  # on receiving a task web-side
    WAITING_FOR_EP = "waiting-for-ep"  # while waiting for ep to accept/be online
    WAITING_FOR_NODES = "waiting-for-nodes"  # jobs are pending at the scheduler
    WAITING_FOR_LAUNCH = "waiting-for-launch"
    EXEC_START = "execution-start"
    EXEC_END = "execution-end"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class InternalTaskState(str, enum.Enum):
    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


class ActorName(str, enum.Enum):
    WORKER = "worker"
    MANAGER = "manager"
    INTERCHANGE = "interchange"
    ENDPOINT = "endpoint"
    RESULT_PROCESSOR = "result-processor"
    WEB_SERVICE = "web-service"
