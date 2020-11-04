from collections import defaultdict
import logging
from typing import Type

from meru.actions import RequireState, StateUpdate
from meru.base import Action, StateNode
from meru.helpers import get_type_from_string
from meru.introspection import discover_state_action_handlers
from meru.sockets import StateConsumerSocket, StateManagerSocket
from meru.types import StateModelType

STATES = dict()
STATE_ACTION_HANDLERS = defaultdict(lambda: list())
logger = logging.getLogger('meru.state')


async def request_state():
    """
    Request states from the state manager. In order for this do have any effect
    all required states have to be registered::

        register_state(SomeState)

    :return: All loaded states
    """
    state_consumer = StateConsumerSocket()

    states_to_request = list(STATES.keys())

    logging.debug(states_to_request)

    action = RequireState(states_to_request)
    await state_consumer.request_state(action)
    state = await state_consumer.receive_state()
    for node in state.nodes:
        STATES[node.__class__] = node

    return STATES


async def answer_state_requests():
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
    if state_cls not in STATES:
        STATES[state_cls] = state_cls()
        for action, handlers in discover_state_action_handlers(STATES[state_cls]).items():
            STATE_ACTION_HANDLERS[action] += handlers
    else:
        logger.warning(f'State {state_cls.__name__} has already been registered.')


def get_all_states():
    return STATES


async def update_state(action: Action):
    if action.__class__ in STATE_ACTION_HANDLERS:
        for method in STATE_ACTION_HANDLERS[action.__class__]:
            method(action)


def get_state(state_cls: StateModelType) -> StateModelType:
    return STATES[state_cls]
