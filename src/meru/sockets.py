import asyncio
import logging

import zmq
import zmq.asyncio

from meru.actions import Action
from meru.handlers import handle_action
from meru.serialization import decode_object, encode_object

PUBLISHER_SOCKET = 'tcp://127.0.0.1:24051'
COLLECTOR_SOCKET = 'tcp://127.0.0.1:24052'
STATE_SOCKET = 'tcp://127.0.0.1:24053'

logger = logging.getLogger('meru.socket')


class MessagingSocket:
    ctx = zmq.asyncio.Context()

    def __init__(self):
        self._socket = None
        self.loop = asyncio.get_event_loop()

    def close(self):
        self._socket.close(linger=0)

    def __del__(self):
        self._socket.close(linger=0)

    @property
    def is_closed(self):
        return self._socket.closed


class PublisherSocket(MessagingSocket):
    def __init__(self):
        super().__init__()
        self._socket = self.ctx.socket(zmq.PUB)
        self._socket.bind(PUBLISHER_SOCKET)
        logger.debug(f'Bound publisher to {PUBLISHER_SOCKET}')

    async def publish(self, action: Action):
        logger.debug('Publishing %s', action)
        logger.info('Got %s', action.__class__.__name__)
        data = [action.topic, encode_object(action)]
        await self._socket.send_multipart(data)


class CollectorSocket(MessagingSocket):
    def __init__(self):
        super().__init__()
        self._socket = self.ctx.socket(zmq.PULL)
        self._socket.bind(COLLECTOR_SOCKET)
        self._socket.setsockopt(zmq.LINGER, 0)
        logger.debug(f'Bound collector to {COLLECTOR_SOCKET}')

    async def collect(self):
        while True:
            data = await self._socket.recv_multipart()
            _, action_data = data
            action = decode_object(action_data)
            logger.debug('Collected %s', action)
            return action


class SubscriberSocket(MessagingSocket):
    def __init__(self):
        super().__init__()
        self._socket = self.ctx.socket(zmq.SUB)
        self._socket.connect(PUBLISHER_SOCKET)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, '')
        self._socket.setsockopt(zmq.LINGER, 0)

        logger.debug(f'Connected subscriber to {PUBLISHER_SOCKET}')

    async def handle_incoming_actions(self):
        while True:
            action = await self.receive_action()
            async for response in handle_action(action):
                yield response

    async def receive_encoded(self):
        return await self._socket.recv_multipart()

    async def receive_action(self):
        data = await self.receive_encoded()
        _, action_data = data
        return decode_object(action_data)


class PushSocket(MessagingSocket):
    def __init__(self):
        super().__init__()
        self._socket = self.ctx.socket(zmq.PUSH)
        self._socket.setsockopt(zmq.LINGER, 0)
        self._socket.connect(COLLECTOR_SOCKET)
        logger.debug(f'Connected pusher to {COLLECTOR_SOCKET}')

    async def push(self, action: Action):
        await self._socket.send_multipart([action.topic, encode_object(action)])


class StateManagerSocket(MessagingSocket):
    def __init__(self):
        super().__init__()
        self._socket = self.ctx.socket(zmq.ROUTER)
        self._socket.setsockopt(zmq.LINGER, 0)
        self._socket.bind(STATE_SOCKET)
        logger.debug(f'Bound state manager to {STATE_SOCKET}')

    async def answer_state_request(self, identity, action):
        logger.debug(f'Sending state update to {identity}')
        self._socket.send_multipart([identity, encode_object(action)])

    async def get_state_request(self):
        while True:
            data = await self._socket.recv_multipart()
            identity, action_data = data
            action = decode_object(action_data)
            return identity, action


class StateConsumerSocket(MessagingSocket):
    def __init__(self):
        super().__init__()
        self._socket = self.ctx.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.LINGER, 0)
        self._socket.connect(STATE_SOCKET)
        logger.debug(f'Connected state consumer to {STATE_SOCKET}')

    async def request_state(self, action):
        await self._socket.send_multipart([encode_object(action)])

    async def receive_state(self):
        data = await self._socket.recv_multipart()
        action = decode_object(data[0])
        return action
