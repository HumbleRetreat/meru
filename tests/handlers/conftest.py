import pytest

from meru.actions import Action
from meru.state import StateNode


@pytest.fixture()
def dummy_action():
    class DummyAction(Action):
        pass
    return DummyAction


@pytest.fixture()
def dummy_state():
    class DummyState(StateNode):
        pass

    return DummyState
