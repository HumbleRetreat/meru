import pytest
from asynctest import create_autospec

from meru.handlers import ActionHandler, handle_action, register_action_handler
from meru.helpers import get_full_path_to_class


def test_register_handler(mocker, dummy_action, dummy_state):
    handlers = mocker.patch('meru.handlers.HANDLERS', {})
    states = mocker.patch('meru.handlers.STATES', {})

    def dummy_handler(action: dummy_action, state: dummy_state):
        pass

    register_action_handler(dummy_handler)

    assert len(handlers) == 1
    assert dummy_action in handlers
    assert handlers[dummy_action] == ActionHandler(dummy_handler, {
        'action': dummy_action,
        'state': dummy_state,
    })

    assert len(states) == 1
    assert get_full_path_to_class(dummy_state) in states


@pytest.mark.asyncio
@pytest.mark.freeze_time
async def test_call_handler(mocker, dummy_action, dummy_state):
    mocker.patch('meru.handlers.HANDLERS', {})
    states = mocker.patch('meru.handlers.STATES', {})

    async def dummy_handler(action: dummy_action, state: dummy_state):
        pass

    stub = create_autospec(dummy_handler)
    register_action_handler(stub)

    await handle_action(dummy_action()).__anext__()

    stub.assert_awaited_once_with(
        action=dummy_action(),
        state=states[get_full_path_to_class(dummy_state)],
    )
