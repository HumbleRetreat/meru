"""Functionality related to action handlers.

The module maintains a global list of registered action handlers.

As the process modules are only loaded when they are run, the list of action handlers gets only
populated by the action handlers of the process that is run.
"""

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
    """Register an action handler.

    This function can be used as an attribute::

        @register_action_handler
        def handle_example_action(action: ExampleAction):
            return AnotherAction()

    Parameters:
        func: The action handler function.
    """
    action, required_states = inspect_action_handler_args(func)
    handler = ActionHandler(func, required_states)
    HANDLERS[action] = handler

    for state_cls in required_states:
        if issubclass(state_cls, StateNode):
            register_state(state_cls)
    return func


async def handle_action(action):
    """Call the registered action handlers that handle ``action``.

    This function does nothing if there is no handler registered for ``action``.

    Parameters:
        action: An object of a class deriving from :py:class:`Action`.

    Yields:
        Actions yielded by the handler, if one is found.
    """
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
    """Periodically checks if the connection to the server is still working.

    :py:class:`Ping` objects are periodically sent to the Broker.  If the connection to the broker
    times out, an exception is raised.

    This function is not used in meru itself, but is inteded to be used by user process
    implementations.

    This function is typically wrapped into an asyncio task::

        import asyncio
        asyncio.create_task(ping_pong())

    Raises:
        :py:class:`PingTimeout`
    """

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
