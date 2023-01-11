"""Application-specific wrappers around ZeroMQ sockets.

This module contains sockets for the implementation of both the broker and other processes.
"""

import asyncio
import logging
from typing import Union

import zmq
import zmq.asyncio
from zmq.ssh import tunnel

from meru.actions import Action
from meru.constants import (
    BIND_ADDRESS,
    BROKER_ADDRESS,
    COLLECTOR_PORT,
    MERU_RECEIVE_TIMEOUT,
    PUBLISHER_PORT,
    SSH_TUNNEL,
    STATE_PORT,
)
from meru.helpers import build_address, get_process_identity
from meru.serialization import decode_object, encode_object

logger = logging.getLogger("meru.socket")


class MessagingSocket:
    """Base class for the other socket classes in this module.

    Attributes:
        ctx: The ZeroMQ context.
        loop: The ZeroMQ event loop.
        is_closed: True if the underlying ZeroMQ socket is closed.
    """

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
    """Broker-side socket for distributing broadcasted :py:class:`Action` objects.

    See Also:
        :py:class:`SubscriberSocket`
    """

    def __init__(self):
        super().__init__()
        address = build_address(BIND_ADDRESS, PUBLISHER_PORT)
        self._socket = self.ctx.socket(zmq.PUB)
        self._socket.bind(address)
        logger.debug(f"Bound publisher to {address}")

    async def publish(self, action: Action):
        """Transmits an action object from the broker to the connected processes."""

        data = [action.topic, encode_object(action)]
        await self._socket.send_multipart(data)


class CollectorSocket(MessagingSocket):
    """Broker-side socket for sending :py:class:`Action` objects to the broker for distribution.

    See Also:
        :py:class:`PushSocket`
    """

    def __init__(self):
        super().__init__()
        bind_address = build_address(BIND_ADDRESS, COLLECTOR_PORT)
        self._socket = self.ctx.socket(zmq.PULL)
        self._socket.bind(bind_address)
        self._socket.setsockopt(zmq.LINGER, 0)
        logger.debug(f"Bound collector to {bind_address}")

    async def collect(self):
        """Receives actions from the connected processes in an endless loop."""
        while True:
            data = await self._socket.recv_multipart()
            _, action_data = data
            action = decode_object(action_data)
            # logger.debug('Collected %s', action)
            return action


class SubscriberSocket(MessagingSocket):
    """Broker-facing socket for receiving the distributed :py:class:`Action` objects.

    See Also:
        :py:class:`PublisherSocket`
    """

    def __init__(self, topics: Union[list, None] = None):
        super().__init__()
        connect_address = build_address(BROKER_ADDRESS, PUBLISHER_PORT)
        self._socket = self.ctx.socket(zmq.SUB)
        if SSH_TUNNEL:
            tunnel.tunnel_connection(self._socket, connect_address, SSH_TUNNEL)
        else:
            self._socket.connect(connect_address)

        if not topics:
            self._socket.setsockopt_string(zmq.SUBSCRIBE, "")
        else:
            for topic in topics:
                self._socket.setsockopt_string(zmq.SUBSCRIBE, topic)

        self._socket.setsockopt(zmq.LINGER, 0)

        logger.debug(f"Connected subscriber to {connect_address}")

    async def handle_incoming_actions(self):
        """Retrieve one received :py:class:`Action` object and calls the registered handlers.

        Yields:
            Actions returned by the handler.
        """
        from meru.handlers import handle_action

        action = await self.receive_action()
        async for response in handle_action(action):
            yield response

    async def receive_encoded(self):
        """Retrieve a single (serialized) action from the socket and return it."""
        return await self._socket.recv_multipart()

    async def receive_action(self):
        """Retrieve a single (serialized) action from the socket and deserialize it."""
        data = await self.receive_encoded()
        _, action_data = data
        return decode_object(action_data)


class PushSocket(MessagingSocket):
    """Broker-facing socket for transmitting :py:class:`Action` objects for distribution.

    See Also:
        :py:class:`CollectorSocket`
    """

    def __init__(self):
        super().__init__()
        connect_address = build_address(BROKER_ADDRESS, COLLECTOR_PORT)
        self._socket = self.ctx.socket(zmq.PUSH)
        self._socket.setsockopt(zmq.LINGER, 0)
        if SSH_TUNNEL:
            tunnel.tunnel_connection(self._socket, connect_address, SSH_TUNNEL)
        else:
            self._socket.connect(connect_address)
        logger.debug(f"Connected pusher to {connect_address}")

    async def push(self, action: Action):
        """Send an action to the broker."""
        await self._socket.send_multipart([action.topic, encode_object(action)])


class StateManagerSocket(MessagingSocket):
    """Broker-side socket for 1:1 communication with the processes.

    In contrast to the :py:class:`PublisherSocket`, :py:class:`Action` objects received by this
    socket are not distributed to the other processes, but answered by the broker directly instead.

    See Also:
        :py:class:`StateConsumerSocket`
    """

    def __init__(self):
        super().__init__()
        bind_address = build_address(BIND_ADDRESS, STATE_PORT)
        self._socket = self.ctx.socket(zmq.ROUTER)
        self._socket.setsockopt(zmq.LINGER, 0)
        self._socket.bind(bind_address)
        logger.debug(f"Bound state manager to {bind_address}")

    async def answer_state_request(self, identity, action):
        """Send an answer to a request for the current state.

        Parameters:
            identity: The  identity of the process that requested the state.
            action: The :py:class:`Action` object to respond with.
        """
        logger.debug(f"Sending state update to {identity}")
        await self._socket.send_multipart([identity, encode_object(action)])

    async def send(self, identity, action):
        """The same as ``self.answer_state_request``"""
        await self._socket.send_multipart([identity, encode_object(action)])

    async def get_state_request(self):
        """Receives a :py:class:`Action` object and deserialize it.

        Returns:
            A tuple that contains the sender process' identity and the received and deserialized
            action.
        """
        data = await self._socket.recv_multipart()
        identity, action_data = data
        action = decode_object(action_data)
        return identity, action


class StateConsumerSocket(MessagingSocket):
    """Broker-facing socket for 1:1 communication.

    See Also:
        :py:class:`StateManagerSocket`
    """

    def __init__(self):
        super().__init__()

        connect_address = build_address(BROKER_ADDRESS, STATE_PORT)
        self._socket = self.ctx.socket(zmq.DEALER)
        self._socket.setsockopt(zmq.LINGER, 0)
        self._socket.setsockopt(zmq.RCVTIMEO, MERU_RECEIVE_TIMEOUT)

        process_id = get_process_identity()

        if process_id:
            self._socket.setsockopt_string(zmq.IDENTITY, process_id)

        if SSH_TUNNEL:
            tunnel.tunnel_connection(self._socket, connect_address, SSH_TUNNEL)
        else:
            self._socket.connect(connect_address)

        logger.debug(f"Connected state consumer to {connect_address}")

    async def send(self, action):
        """Send an :py:class:`Action` object to the broker.

        Parameters:
            action: The action to send.
        """
        await self._socket.send_multipart([encode_object(action)])

    async def receive(self):
        """Receives an :py:class:`Action` object back from the broker."""
        data = await self._socket.recv_multipart()
        action = decode_object(data[0])
        return action
