import pytest

from meru.exceptions import HandlerException
from meru.introspection import inspect_action_handler_args


def test_successful_inspection_action_and_state(dummy_action, dummy_state_cls):
    def handle_dummy_action(action: dummy_action, files: dummy_state_cls):
        pass

    action, required_states = inspect_action_handler_args(handle_dummy_action)

    assert len(required_states) == 1
    assert action == dummy_action
    assert dummy_state_cls in required_states


def test_successful_inspection_only_action(dummy_action):
    def handle_dummy_action(action: dummy_action):
        pass

    action, required_states = inspect_action_handler_args(handle_dummy_action)

    assert len(required_states) == 0
    assert action == dummy_action


def test_successful_inspection_multiple_states(dummy_action, dummy_state_cls):
    class dummy_state_cls2(dummy_state_cls):
        pass

    def handle_dummy_action(
        action: dummy_action, state1: dummy_state_cls, state2: dummy_state_cls2
    ):
        pass

    action, required_states = inspect_action_handler_args(handle_dummy_action)

    assert len(required_states) == 2
    assert action == dummy_action
    assert dummy_state_cls in required_states
    assert dummy_state_cls2 in required_states


def test_prevent_injection_of_identical_state(dummy_action, dummy_state_cls):
    def handle_dummy_action(
        action: dummy_action, state1: dummy_state_cls, state2: dummy_state_cls
    ):
        pass

    with pytest.raises(HandlerException) as exc:
        inspect_action_handler_args(handle_dummy_action)

    assert (
        str(exc.value)
        == "Type 'DummyState' has been added twice to handler 'handle_dummy_action'. This is not possible."
    )


def test_failed_inspection_too_many_actions(dummy_action):
    def handle_dummy_action(action: dummy_action, action2: dummy_action):
        pass

    with pytest.raises(HandlerException) as exc:
        inspect_action_handler_args(handle_dummy_action)

    assert str(exc.value) == "An action handler can have only one action."


def test_failed_inspection_no_action(dummy_state_cls):
    def handle_dummy_action(state1: dummy_state_cls):
        pass

    with pytest.raises(HandlerException) as exc:
        inspect_action_handler_args(handle_dummy_action)

    assert str(exc.value) == "An action handler needs one action."


def test_failed_inspection_invalid_type(dummy_state_cls):
    def handle_dummy_action(action: str):
        pass

    with pytest.raises(HandlerException) as exc:
        inspect_action_handler_args(handle_dummy_action)

    assert (
        "An action handler can only have Actions and StateNodes as calling args"
        in str(exc.value)
    )
