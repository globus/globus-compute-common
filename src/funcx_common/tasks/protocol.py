import typing as t

from .constants import TaskState


# use of typing.Protocol requires python3.8
# since some parts of funcX support current pythons (py3.6, py3.8), we'll
# define the protocol as a normal class for simplicity for now
#
# TODO: evaluate conditional requirement for typing_extensions to allow the use
# of typing.Protocol
class TaskProtocol:
    task_id: str
    endpoint: t.Optional[str]
    status: TaskState
