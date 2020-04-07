import pytest

from meru.helpers import inspect_action_handler


def test_successful_inspection_action_and_state(dummy_action, dummy_state):
    def handle_dummy_action(action: dummy_action, files: dummy_state):
        pass

    action, calling_args = inspect_action_handler(handle_dummy_action)

    assert len(calling_args) == 2
    assert action == dummy_action
    assert calling_args['action'] == dummy_action
    assert calling_args['files'] == dummy_state


def test_successful_inspection_only_action(dummy_action):
    def handle_dummy_action(action: dummy_action):
        pass

    action, calling_args = inspect_action_handler(handle_dummy_action)

    assert len(calling_args) == 1
    assert action == dummy_action
    assert calling_args['action'] == dummy_action


def test_successful_inspection_multiple_states(dummy_action, dummy_state):
    def handle_dummy_action(action: dummy_action, state1: dummy_state, state2: dummy_state):
        pass

    action, calling_args = inspect_action_handler(handle_dummy_action)

    assert len(calling_args) == 3
    assert action == dummy_action
    assert calling_args['action'] == dummy_action
    assert calling_args['state1'] == dummy_state
    assert calling_args['state2'] == dummy_state


def test_failed_inspection_too_many_actions(dummy_action):
    def handle_dummy_action(action: dummy_action, action2: dummy_action):
        pass

    with pytest.raises(Exception) as exc:
        inspect_action_handler(handle_dummy_action)

    assert str(exc.value) == 'An action handler can have only one action.'


def test_failed_inspection_no_action():
    def handle_dummy_action(action: str):
        pass

    with pytest.raises(Exception) as exc:
        inspect_action_handler(handle_dummy_action)

    assert str(exc.value) == 'An action handler needs one action.'
