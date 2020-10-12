import logging

from meru.handlers import get_state, register_state


def test_register_state(dummy_action, dummy_state_cls, mocker):
    states = mocker.patch('meru.handlers.STATES', {})
    state_action_handlers = mocker.patch('meru.handlers.STATE_ACTION_HANDLERS', {})

    register_state(dummy_state_cls)

    state_object = get_state(dummy_state_cls)

    assert isinstance(state_object, dummy_state_cls)

    assert len(states) == 1
    assert isinstance(states[dummy_state_cls], dummy_state_cls)

    assert len(state_action_handlers) == 1
    assert len(state_action_handlers[dummy_state_cls]) == 1
    assert state_action_handlers[dummy_state_cls][dummy_action] == [state_object.handle_dummy_action]


def test_register_state_warn_if_multiple_registrations(caplog, dummy_state_cls, mocker):
    caplog.set_level(logging.WARNING)
    states = mocker.patch('meru.handlers.STATES', {})
    state_action_handlers = mocker.patch('meru.handlers.STATE_ACTION_HANDLERS', {})

    register_state(dummy_state_cls)
    register_state(dummy_state_cls)

    assert 'has already been registered' in caplog.text
