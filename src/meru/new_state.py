from collections import defaultdict
from dataclasses import dataclass, field
import inspect
from typing import Type, Union, get_origin

from meru.actions import Action
from meru.types import MeruObject


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


def discover_action_handlers(state_node: Type[NewStateModel]):
    handlers = defaultdict(lambda: [])

    b = inspect.getmembers(state_node)
    for (name, foo) in b:
        if inspect.ismethod(foo):
            signature = inspect.signature(foo)
            for param in signature.parameters.values():
                if get_origin(param.annotation) is Union:
                    pass
                elif issubclass(param.annotation, Action):
                    handlers[param.annotation].append(foo)
    return handlers


states = {}
_handlers = {}


def register_state(foo: Type[NewStateModel]):
    global _handlers, states
    states[foo] = foo()
    _handlers = discover_action_handlers(states[foo])


def update_state(action: Action):
    global _handlers
    for method in _handlers[action.__class__]:
        method(action)


def get_state(state_node):
    global states
    a = states
    return states[state_node]
