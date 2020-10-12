from dataclasses import dataclass
from importlib import import_module
import inspect
from typing import List

from meru.base import Action, StateNode


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
