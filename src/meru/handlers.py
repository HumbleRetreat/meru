import asyncio
import inspect
import logging
from collections import namedtuple

from zmq import Again

from meru.actions import Action, Ping, RequireState
from meru.exceptions import PingTimeout
from meru.helpers import get_full_path_to_class, inspect_action_handler
from meru.state import StateNode

HANDLERS = dict()
STATES = dict()
STATE_HANDLER_MAPPING = dict()

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


def register_state(state_cls):
    cls_path = get_full_path_to_class(state_cls)
    if state_cls not in STATES:
        STATES[cls_path] = state_cls()


def get_all_states():
    return STATES


def map_calling_args(calling_args: dict, action):
    args = {}

    for arg, cls in calling_args.items():
        if issubclass(cls, StateNode):
            args[arg] = STATES[get_full_path_to_class(cls)]

        if issubclass(cls, Action):
            args[arg] = action

    return args


async def update_state(action: Action):
    for state in STATES.values():
        state.process_action(action)


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


def get_state(state_cls):
    return STATES[get_full_path_to_class(state_cls)]


async def request_state():
    from meru.sockets import StateConsumerSocket
    state_consumer = StateConsumerSocket()

    states_to_request = list(STATES.keys())

    logging.debug(states_to_request)

    action = RequireState(states_to_request)
    await state_consumer.send(action)
    state = await state_consumer.receive()
    for node in state.nodes:
        class_path = get_full_path_to_class(node.__class__)
        STATES[class_path] = node

    state_consumer.close()

    return STATES


async def ping_pong():
    from meru.sockets import StateConsumerSocket
    state_consumer = StateConsumerSocket()

    while True:
        action = Ping()
        await state_consumer.send(action)

        try:
            await state_consumer.receive()
        except Again:
            raise PingTimeout() from None

        await asyncio.sleep(10)
