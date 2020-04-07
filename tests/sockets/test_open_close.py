import pytest

from meru.sockets import CollectorSocket, PublisherSocket, PushSocket, StateConsumerSocket, StateManagerSocket, \
    SubscriberSocket


@pytest.mark.asyncio
@pytest.mark.parametrize('socket_cls', [
    CollectorSocket,
    PushSocket,
    PublisherSocket,
    StateConsumerSocket,
    StateManagerSocket,
    SubscriberSocket,
])
async def test_socket_open(socket_cls, wait):
    socket = socket_cls()
    await wait()

    assert socket.is_closed is False
    socket.close()


@pytest.mark.asyncio
@pytest.mark.parametrize('socket_cls', [
    CollectorSocket,
    PushSocket,
    PublisherSocket,
    StateConsumerSocket,
    StateManagerSocket,
    SubscriberSocket,
])
async def test_socket_close(socket_cls, wait):
    socket = socket_cls()
    await wait()

    socket.close()
    await wait()

    assert socket.is_closed is True
