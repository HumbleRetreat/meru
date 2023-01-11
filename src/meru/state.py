"""Functionality related to state management.

This module maintains a global list of :py:class:`StateNode` objects.
"""
from collections import defaultdict
import logging
from typing import Type

from meru.actions import RequireState, StateUpdate
from meru.base import Action, StateNode
from meru.helpers import get_type_from_string
from meru.introspection import discover_state_action_handlers
from meru.sockets import StateConsumerSocket, StateManagerSocket
from meru.types import StateModelType

STATES = {}
STATE_ACTION_HANDLERS = defaultdict(lambda: [])
logger = logging.getLogger("meru.state")


async def request_states():
    """
    Request states from the state manager. In order for this do have any effect
    all required states have to be registered::

        register_state(SomeState)

    Used by the processes.

    Returns:
        All loaded states
    """
    state_consumer = StateConsumerSocket()

    states_to_request = list(STATES.keys())

    action = RequireState(states_to_request)
    await state_consumer.send(action)

    state = await state_consumer.receive()

    for node in state.nodes:
        STATES[node.__class__] = node
        logging.info(f"Loaded state from broker: {node.__class__.__name__}")

    return STATES


async def answer_state_requests():
    """Answer incoming state requests.

    Start an endless loop that listens for state update requests and answer them.  Meru does not
    call the function itself, but a broker implementation probably wants to use this or a similar
    implementation.

    This coroutine is probably most often run in a separate ``asyncio`` task::

        import asyncio
        asyncio.create_task(answer_state_requests())
    """
    state_manager = StateManagerSocket()

    while True:
        identity, action = await state_manager.get_state_request()
        nodes = []
        states = get_all_states()
        for node in action.nodes:
            node_cls = get_type_from_string(node)
            nodes.append(states[node_cls])

        action = StateUpdate(nodes)
        await state_manager.answer_state_request(identity, action)


def register_state(state_cls: Type[StateNode]):
    """Add a state to the list of registered states.

    This needs to get called at process initialization for every :py:class:`StateNode` that the
    process plans on using.
    """
    if state_cls not in STATES:
        STATES[state_cls] = state_cls()
        for action, handlers in discover_state_action_handlers(
            STATES[state_cls]
        ).items():
            STATE_ACTION_HANDLERS[action] += handlers
    else:
        pass


def get_all_states():
    """Returns the global list of states."""
    return STATES


async def update_state(action: Action):
    """Calls the state update handlers that are triggered by an :py:class:`Action` oject.

    Parameters:
        action: The action.
    """
    if action.__class__ in STATE_ACTION_HANDLERS:
        for method in STATE_ACTION_HANDLERS[action.__class__]:
            method(action)


def get_state(state_cls: StateModelType) -> StateModelType:
    """Get the instance of the given :py:class:`StateNode` used by this process.

    Parameters:
        state_cls: The class object of the requested state object.

    Returns:
        The instance local to this process.
    """
    return STATES[state_cls]
