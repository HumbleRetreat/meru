import logging

import pytest

from meru.state import (
    answer_state_requests,
    get_all_states,
    get_state,
    register_state,
    request_states,
    update_state,
)


def test_register_state(
    dummy_action, dummy_state_cls, mocked_states, mocked_state_action_handlers
):
    register_state(dummy_state_cls)

    state_object = get_state(dummy_state_cls)

    assert isinstance(state_object, dummy_state_cls)

    assert len(mocked_states) == 1
    assert isinstance(mocked_states[dummy_state_cls], dummy_state_cls)

    assert len(mocked_state_action_handlers) == 1
    assert len(mocked_state_action_handlers[dummy_state_cls]) == 0
    assert mocked_state_action_handlers[dummy_action] == []


def test_get_all_states(dummy_state_cls):
    register_state(dummy_state_cls)

    all_states = get_all_states()

    assert all_states == {dummy_state_cls: dummy_state_cls()}


@pytest.mark.asyncio
async def test_update_state(dummy_state_cls, dummy_action_with_field):
    register_state(dummy_state_cls)

    action = dummy_action_with_field("some_field_value")

    await update_state(action)

    state = get_state(dummy_state_cls)

    assert state.state_field == "some_field_value"


@pytest.mark.asyncio
async def test_state_request_cycle(event_loop, dummy_state_cls, wait):
    register_state(dummy_state_cls)

    task = event_loop.create_task(answer_state_requests())

    await wait()

    loaded_states = await request_states()

    assert loaded_states == {dummy_state_cls: dummy_state_cls(state_field="")}

    task.cancel()
    await wait()
