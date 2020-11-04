from collections import namedtuple
import inspect

from meru.actions import Action
from meru.base import StateNode
from meru.introspection import inspect_action_handler
from meru.state import get_state, register_state, update_state

HANDLERS = dict()

ActionHandler = namedtuple('ActionHandler', 'func calling_args')


def register_action_handler(func):
    action, calling_args = inspect_action_handler(func)
    handler = ActionHandler(func, calling_args)
    HANDLERS[action] = handler

    for state_cls in calling_args.values():
        if not issubclass(state_cls, StateNode):
            continue

        register_state(state_cls)
    return func


def map_calling_args(calling_args: dict, action):
    args = {}

    for arg, cls in calling_args.items():
        if issubclass(cls, StateNode):
            args[arg] = get_state(cls)

        if issubclass(cls, Action):
            args[arg] = action

    return args


async def handle_action(action):
    action_cls = action.__class__
    handler = HANDLERS.get(action_cls, None)

    await update_state(action)

    if not handler:
        return

    handler_args = map_calling_args(handler.calling_args, action)

    if inspect.isasyncgenfunction(handler.func):
        async for action in handler.func(**handler_args):
            yield action
    else:
        yield await handler.func(**handler_args)
