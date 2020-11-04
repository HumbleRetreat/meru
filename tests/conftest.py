import asyncio
from collections import defaultdict
from dataclasses import dataclass, field

import pytest

from meru.base import Action, MeruObject, StateNode
from meru.sockets import StateConsumerSocket, StateManagerSocket


@dataclass
class DummyObject(MeruObject):
    pass


@dataclass
class DummyAction(Action):
    pass


@dataclass
class DummyActionWithField(Action):
    field: str


@dataclass
class DummyState(StateNode):
    state_field: str = field(default='')

    def handle_dummy_action(self, action: DummyActionWithField):
        self.state_field = action.field


@pytest.fixture(autouse=True, scope='function')
def mocked_state_action_handlers(mocker):
    return mocker.patch('meru.state.STATE_ACTION_HANDLERS', defaultdict(lambda: list()))


@pytest.fixture(autouse=True, scope='function')
def mocked_states(mocker):
    return mocker.patch('meru.state.STATES', {})


@pytest.yield_fixture()
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop


@pytest.fixture()
def wait():
    def gen_sleep():
        return asyncio.sleep(0.1)

    return gen_sleep


@pytest.fixture()
def dummy_object():
    return DummyObject


@pytest.fixture()
def dummy_action():
    return DummyAction


@pytest.fixture()
def dummy_action_with_field():
    return DummyActionWithField


@pytest.fixture()
def dummy_state_cls():
    return DummyState


@pytest.fixture()
def state_manager():
    socket = StateManagerSocket()
    yield socket
    socket.close()


@pytest.fixture()
def state_consumer():
    socket = StateConsumerSocket()
    yield socket
    socket.close()
