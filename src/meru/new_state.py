from collections import defaultdict
from dataclasses import dataclass, field
import inspect
from typing import get_args, Type, TypeVar, Union, get_origin

from meru.actions import Action
from meru.types import MeruObject


StateModelType = TypeVar('StateModelType')


@dataclass
class SomeAction(Action):
    foo: str


class SomeOtherAction(Action):
    lol: int


@dataclass
class NewStateModel(MeruObject):
    pass


@dataclass
class SomeState(NewStateModel):
    bar: str = field(default='')

    def handle_something(self, action: SomeAction):
        self.bar = action.foo

    def handle_all(self, action: Union[SomeAction, SomeOtherAction]):
        pass


states = {}
_handlers = {}


def update_state(action: Action):
    global _handlers
    for method in _handlers[action.__class__]:
        method(action)


def get_state(state_node: StateModelType) -> StateModelType:
    global states
    a = states
    return states[state_node]
