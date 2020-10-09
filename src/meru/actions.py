from dataclasses import dataclass, field
from importlib import import_module
import inspect
import time
from typing import List

from meru.helpers import underscore
from meru.state import StateNode
from meru.types import MeruObject


@dataclass
class Action(MeruObject):
    topic = b''

    timestamp: float = field(
        init=False,
        repr=False,
    )

    def __post_init__(self):
        self.timestamp = time.time()

    @classmethod
    def handler_name(cls):
        cls_name = cls.__name__
        return 'handle_' + underscore(cls_name)


@dataclass
class StateUpdate(Action):
    topic = b'StateUpdate'

    nodes: List[StateNode]


@dataclass
class RequireState(Action):
    topic = b'state'

    nodes: List[str]


_all_actions = {}


def discover_actions(path):
    mod = import_module(path)

    for name, cls in inspect.getmembers(mod, inspect.isclass):
        if issubclass(cls, Action):
            _all_actions[cls.__name__] = cls


def get_all_actions():
    return _all_actions


def get_all_actions_names():
    return _all_actions.keys()
