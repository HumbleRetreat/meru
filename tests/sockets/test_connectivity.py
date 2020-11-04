import pytest

from meru.actions import RequireState, StateUpdate
from meru.sockets import CollectorSocket, PublisherSocket, PushSocket, StateConsumerSocket, StateManagerSocket, \
    SubscriberSocket
import meru.state


@pytest.mark.asyncio
@pytest.mark.freeze_time
async def test_push_to_collector(dummy_action, wait):
    pusher = PushSocket()
    await wait()

    collector = CollectorSocket()
    await wait()

    await pusher.push(dummy_action())
    await wait()

    result = await collector.collect()

    assert result == dummy_action()

    pusher.close()
    collector.close()
    await wait()


@pytest.mark.asyncio
@pytest.mark.freeze_time
async def test_publisher_to_subscriber(dummy_action, wait):
    publisher = PublisherSocket()
    await wait()

    subscriber = SubscriberSocket()
    await wait()

    await publisher.publish(dummy_action())
    await wait()

    sub_result = await subscriber.receive_action()
    assert sub_result == dummy_action()

    publisher.close()
    subscriber.close()
    await wait()


@pytest.mark.asyncio
@pytest.mark.freeze_time
async def test_state_manager_to_state_consumer(state_manager, state_consumer, wait):
    action = RequireState([])
    await state_consumer.request_state(action)

    identity, action = await state_manager.get_state_request()
    action = StateUpdate([])
    await state_manager.answer_state_request(identity, action)

    state = await state_consumer.receive_state()

    assert state == StateUpdate([])
