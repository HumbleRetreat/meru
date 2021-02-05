import asyncio
import logging
import os
import socket

import zmq
import zmq.asyncio
from zmq.ssh import tunnel

from meru.actions import Action
from meru.constants import BIND_ADDRESS, BROKER_ADDRESS, COLLECTOR_PORT, PUBLISHER_PORT, SSH_TUNNEL, STATE_PORT
from meru.handlers import handle_action
from meru.helpers import build_address
from meru.serialization import decode_object, encode_object

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
        address = build_address(BIND_ADDRESS, PUBLISHER_PORT)
        self._socket = self.ctx.socket(zmq.PUB)
        self._socket.bind(address)
        logger.debug(f'Bound publisher to {address}')

    async def publish(self, action: Action):
        data = [action.topic, encode_object(action)]
        await self._socket.send_multipart(data)


class CollectorSocket(MessagingSocket):
    def __init__(self):
        super().__init__()
        bind_address = build_address(BIND_ADDRESS, COLLECTOR_PORT)
        self._socket = self.ctx.socket(zmq.PULL)
        self._socket.bind(bind_address)
        self._socket.setsockopt(zmq.LINGER, 0)
        logger.debug(f'Bound collector to {bind_address}')

    async def collect(self):
        while True:
            data = await self._socket.recv_multipart()
            _, action_data = data
            action = decode_object(action_data)
            # logger.debug('Collected %s', action)
            return action


class SubscriberSocket(MessagingSocket):
    def __init__(self):
        super().__init__()
        connect_address = build_address(BROKER_ADDRESS, PUBLISHER_PORT)
        self._socket = self.ctx.socket(zmq.SUB)
        if SSH_TUNNEL:
            tunnel.tunnel_connection(self._socket, connect_address, SSH_TUNNEL)
        else:
            self._socket.connect(connect_address)
        self._socket.setsockopt_string(zmq.SUBSCRIBE, '')
        self._socket.setsockopt(zmq.LINGER, 0)

        logger.debug(f'Connected subscriber to {connect_address}')

    async def handle_incoming_actions(self):
        while True:
            action = await self.receive_action()
            async for response in handle_action(action):
                yield response

    async def receive_encoded(self):
        try:
            return await self._socket.recv_multipart()
        except Exception as e:
            print(e)

    async def receive_action(self):
        data = await self.receive_encoded()
        _, action_data = data
        return decode_object(action_data)


class PushSocket(MessagingSocket):
    def __init__(self):
        super().__init__()
        connect_address = build_address(BROKER_ADDRESS, COLLECTOR_PORT)
        self._socket = self.ctx.socket(zmq.PUSH)
        self._socket.setsockopt(zmq.LINGER, 0)
        if SSH_TUNNEL:
            tunnel.tunnel_connection(self._socket, connect_address, SSH_TUNNEL)
        else:
            self._socket.connect(connect_address)
        logger.debug(f'Connected pusher to {connect_address}')

    async def push(self, action: Action):
        await self._socket.send_multipart([action.topic, encode_object(action)])


class StateManagerSocket(MessagingSocket):
    def __init__(self):
        super().__init__()
        bind_address = build_address(BIND_ADDRESS, STATE_PORT)
        self._socket = self.ctx.socket(zmq.ROUTER)
        self._socket.setsockopt(zmq.LINGER, 0)
        self._socket.bind(bind_address)
        logger.debug(f'Bound state manager to {bind_address}')

    async def answer_state_request(self, identity, action):
        logger.debug(f'Sending state update to {identity.decode()}')
        self._socket.send_multipart([identity, encode_object(action)])

    async def send(self, identity, action):
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

        connect_address = build_address(BROKER_ADDRESS, STATE_PORT)
        self._socket = self.ctx.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.LINGER, 0)
        self._socket.setsockopt(zmq.RCVTIMEO, 2000)

        process_name = os.environ.get('MERU_PROCESS', None)

        if process_name:
            hostname = socket.gethostname()
            self._socket.setsockopt_string(zmq.IDENTITY, f'{hostname}-{process_name}')

        if SSH_TUNNEL:
            tunnel.tunnel_connection(self._socket, connect_address, SSH_TUNNEL)
        else:
            self._socket.connect(connect_address)

        logger.debug(f'Connected state consumer to {connect_address}')

    async def send(self, action):
        await self._socket.send_multipart([encode_object(action)])

    async def receive(self):
        data = await self._socket.recv_multipart()
        action = decode_object(data[0])
        return action
