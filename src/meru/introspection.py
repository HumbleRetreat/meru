from collections import defaultdict
from functools import lru_cache
import inspect
from typing import Type, Union, get_args, get_origin

from meru.base import Action, MeruObject, StateNode


def discover_state_action_handlers(state_node: Type[StateNode]):
    handlers = defaultdict(lambda: [])

    b = inspect.getmembers(state_node)
    for (name, foo) in b:
        if inspect.ismethod(foo):
            signature = inspect.signature(foo)
            for param in signature.parameters.values():
                if get_origin(param.annotation) is Union:
                    for t in get_args(param.annotation):
                        handlers[t].append(foo)
                elif issubclass(param.annotation, Action):
                    handlers[param.annotation].append(foo)
    return handlers


def inspect_action_handler(func):

    found_action = None
    calling_args = {}
    signature = inspect.signature(func)

    for param in signature.parameters.values():
        if issubclass(param.annotation, Action):
            if found_action is not None:
                raise Exception('An action handler can have only one action.')
            found_action = param.annotation
            calling_args[param.name] = param.annotation
        elif issubclass(param.annotation, StateNode):
            calling_args[param.name] = param.annotation

    if found_action is None:
        raise Exception('An action handler needs one action.')

    return found_action, calling_args


@lru_cache(maxsize=None)
def get_class_init_args(cls: Type[MeruObject]):
    args = inspect.getfullargspec(cls.__init__)
    init_args = args.args[:]
    init_args.remove('self')

    return init_args


@lru_cache(maxsize=None)
def get_subclasses(base_cls: type):
    all_subclasses = {}

    def _get_all_subclasses(cls):
        for subclass in cls.__subclasses__():
            _get_all_subclasses(subclass)
            all_subclasses[subclass.__name__] = subclass

    if len(all_subclasses) == 0:
        _get_all_subclasses(base_cls)

    return all_subclasses
