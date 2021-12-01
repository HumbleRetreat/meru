import pytest

from meru.actions import RequireState, StateUpdate
from meru.sockets import CollectorSocket, PublisherSocket, PushSocket, SubscriberSocket


@pytest.mark.asyncio
async def test_push_to_collector(dummy_action, wait):
    collector = CollectorSocket()
    await wait()

    pusher = PushSocket()
    await wait()

    action = dummy_action()

    await pusher.push(action)
    await wait()

    result = await collector.collect()

    assert result == action

    pusher.close()
    collector.close()
    await wait()


@pytest.mark.asyncio
async def test_publisher_to_subscriber(dummy_action, wait):
    publisher = PublisherSocket()
    await wait()

    subscriber = SubscriberSocket()
    await wait()

    action = dummy_action()

    await publisher.publish(action)
    await wait()

    sub_result = await subscriber.receive_action()
    assert sub_result == action

    publisher.close()
    subscriber.close()
    await wait()


@pytest.mark.asyncio
async def test_state_manager_to_state_consumer(state_manager, state_consumer, wait):
    action = RequireState([])
    await state_consumer.send(action)

    identity, action = await state_manager.get_state_request()
    action = StateUpdate([])
    await state_manager.answer_state_request(identity, action)

    state = await state_consumer.receive()

    assert state == action
