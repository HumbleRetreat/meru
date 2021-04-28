from dataclasses import dataclass
from importlib import import_module
import inspect
from typing import List

from meru.base import Action, StateNode
from meru.helpers import get_full_path_to_class


@dataclass
class StateUpdate(Action):
    topic = b'StateUpdate'

    nodes: List[StateNode]


@dataclass
class Ping(Action):
    pass


@dataclass
class Pong(Action):
    pass


@dataclass
class RequireState(Action):
    topic = b'state'

    nodes: List[str]

    def to_dict(self):
        sup = super().to_dict()
        sup['nodes'] = [get_full_path_to_class(obj) for obj in sup['nodes']]
        return sup


_all_actions = {}


def discover_actions(path):
    mod = import_module(path)

    for name, cls in inspect.getmembers(mod, inspect.isclass):
        if issubclass(cls, Action):
            _all_actions[cls.__name__] = cls


def get_all_actions():
    return _all_actions
