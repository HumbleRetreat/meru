from unittest.mock import create_autospec
import pytest

from meru.handlers import handle_action, register_action_handler


@pytest.mark.asyncio
async def test_dont_handle_unknown_action(dummy_action):
    with pytest.raises(StopAsyncIteration):
        await handle_action(dummy_action()).__anext__()


@pytest.mark.xfail
@pytest.mark.asyncio
@pytest.mark.freeze_time
async def test_handle_async_generator_handler(
    dummy_action, dummy_state_cls, mocker, mocked_states
):
    """
    This test will fail, because I have no idea how to create a stub with annotations.
    """
    mocker.patch("meru.handlers.HANDLERS", {})

    async def dummy_handler(action: dummy_action, state: dummy_state_cls):
        yield dummy_action()

    stub = create_autospec(dummy_handler)
    register_action_handler(stub)

    await handle_action(dummy_action()).__anext__()

    stub.assert_awaited_once_with(
        action=dummy_action(),
        state=mocked_states[dummy_state_cls],
    )
