from unittest.mock import create_autospec

import pytest

from meru.handlers import ActionHandler, handle_action, register_action_handler


def test_register_handler(mocker, dummy_action, dummy_state_cls, mocked_states):
    handlers = mocker.patch('meru.handlers.HANDLERS', {})

    def dummy_handler(action: dummy_action, state: dummy_state_cls):
        pass

    register_action_handler(dummy_handler)

    assert len(handlers) == 1
    assert dummy_action in handlers
    assert handlers[dummy_action] == ActionHandler(dummy_handler, {
        'action': dummy_action,
        'state': dummy_state_cls,
    })

    assert len(mocked_states) == 1
    assert dummy_state_cls in mocked_states


@pytest.mark.asyncio
@pytest.mark.freeze_time
async def test_call_handler(mocker, dummy_action, dummy_state_cls, mocked_states):
    mocker.patch('meru.handlers.HANDLERS', {})

    async def dummy_handler(action: dummy_action, state: dummy_state_cls):
        pass

    stub = create_autospec(dummy_handler)
    register_action_handler(stub)

    await handle_action(dummy_action()).__anext__()

    stub.assert_awaited_once_with(
        action=dummy_action(),
        state=mocked_states[dummy_state_cls],
    )
