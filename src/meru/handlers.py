import asyncio
import inspect
from collections import namedtuple

from zmq import Again

from meru.actions import Ping
from meru.exceptions import PingTimeout
from meru.introspection import inspect_action_handler_args
from meru.state import StateNode, get_state, register_state, update_state

HANDLERS = {}

ActionHandler = namedtuple("ActionHandler", "func calling_args")


def register_action_handler(func):
    action, required_states = inspect_action_handler_args(func)
    handler = ActionHandler(func, required_states)
    HANDLERS[action] = handler

    for state_cls in required_states:
        if issubclass(state_cls, StateNode):
            register_state(state_cls)
    return func


async def handle_action(action):
    action_cls = action.__class__
    handler = HANDLERS.get(action_cls, None)

    await update_state(action)

    if not handler:
        return

    states_to_inject = [get_state(cls) for cls in handler.calling_args]

    if inspect.isasyncgenfunction(handler.func):
        async for action in handler.func(action, *states_to_inject):
            yield action
    else:
        yield await handler.func(action, *states_to_inject)


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
