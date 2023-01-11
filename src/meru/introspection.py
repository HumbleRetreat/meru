import inspect
from collections import defaultdict
from functools import lru_cache
from typing import Type, Union, get_args, get_origin

from meru.base import Action, StateNode
from meru.exceptions import HandlerException


def discover_state_action_handlers(state_node: Type[StateNode]):
    handlers = defaultdict(lambda: [])

    members = inspect.getmembers(state_node)
    for (_, value) in members:
        if inspect.ismethod(value):
            signature = inspect.signature(value)
            for param in signature.parameters.values():
                if get_origin(param.annotation) is Union:
                    for argument in get_args(param.annotation):
                        handlers[argument].append(value)
                elif issubclass(param.annotation, Action):
                    handlers[param.annotation].append(value)
    return handlers


def inspect_action_handler_args(func: callable):
    """
    Inspects and action handler's calling arguments. An action handler can only have one
    action and state nodes as calling arguments. Calling args need to be annotated in order
    to be recognized. Having any other type or no type at all will raise an exception.

    This will be fine::

        async def do_something(action: SomeActionClass, some_state: SomeStateClass):
            pass

    This will not be fine, action is not annotated, some_param has an invalid type::

        async def do_something(action, some_param: int):
            pass

    Parameters:
        func:

    Returns:
    """
    found_action = None
    required_states = set()
    signature = inspect.signature(func)

    for param in signature.parameters.values():
        if issubclass(param.annotation, Action):
            if found_action is not None:
                raise HandlerException("An action handler can have only one action.")
            found_action = param.annotation
        elif issubclass(param.annotation, StateNode):
            if param.annotation in required_states:
                raise HandlerException(
                    f"Type '{param.annotation.__name__}' has been added twice to handler '{func.__name__}'. "
                    f"This is not possible."
                )
            required_states.add(param.annotation)
        else:
            raise HandlerException(
                f"Error registering {func.__name__}. "
                f"An action handler can only have Actions and StateNodes as calling args. "
                f"'{param}' is invalid."
            )

    if found_action is None:
        raise HandlerException("An action handler needs one action.")

    return found_action, required_states


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
