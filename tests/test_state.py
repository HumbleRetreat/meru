import logging

import pytest

from meru.handlers import get_all_states, get_state, register_state, request_state, update_state
from meru.sockets import StateConsumerSocket, StateManagerSocket


def test_register_state(dummy_action, dummy_state_cls, mocked_states, mocked_state_action_handlers):
    register_state(dummy_state_cls)

    state_object = get_state(dummy_state_cls)

    assert isinstance(state_object, dummy_state_cls)

    assert len(mocked_states) == 1
    assert isinstance(mocked_states[dummy_state_cls], dummy_state_cls)

    assert len(mocked_state_action_handlers) == 1
    assert len(mocked_state_action_handlers[dummy_state_cls]) == 0
    assert mocked_state_action_handlers[dummy_action] == []


def test_register_state_warn_if_multiple_registrations(caplog, dummy_state_cls):
    caplog.set_level(logging.WARNING)

    register_state(dummy_state_cls)
    register_state(dummy_state_cls)

    assert 'has already been registered' in caplog.text


def test_get_all_states(dummy_state_cls):
    register_state(dummy_state_cls)

    all_states = get_all_states()

    assert all_states == {dummy_state_cls: dummy_state_cls()}


@pytest.mark.asyncio
async def test_update_state(dummy_state_cls, dummy_action_with_field):
    register_state(dummy_state_cls)

    action = dummy_action_with_field('some_field_value')

    await update_state(action)

    state = get_state(dummy_state_cls)

    assert state.state_field == 'some_field_value'
