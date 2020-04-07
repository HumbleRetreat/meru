import pytest

from meru.sockets import CollectorSocket, PublisherSocket, PushSocket, SubscriberSocket


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
