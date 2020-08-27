from dataclasses import dataclass, field
import datetime
from importlib import import_module
import inspect
from typing import List

from meru.helpers import underscore
from meru.state import StateNode


@dataclass
class Action:
    topic = b''

    timestamp: datetime.datetime = field(
        init=False,
        repr=False,
    )

    def __post_init__(self):
        self.timestamp = datetime.datetime.now()

    @classmethod
    def handler_name(cls):
        cls_name = cls.__name__
        return 'handle_' + underscore(cls_name)

    @property
    def action_type(self) -> str:
        return self.__class__.__name__

    def to_dict(self):
        data = self.__dict__
        data['action_type'] = self.action_type
        return data


@dataclass
class StateUpdate(Action):
    topic = b'StateUpdate'

    nodes: List[StateNode]


@dataclass
class RequireState(Action):
    topic = b'state'

    nodes: List[str]


def discover_actions(path):
    mod = import_module(path)

    for name, cls in inspect.getmembers(mod, inspect.isclass):
        if issubclass(cls, Action):
            pass

def get_all_actions():
    pass
