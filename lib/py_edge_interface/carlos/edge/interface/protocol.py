"""This module defines an abstract protocol that can be be implemented by either the
server and client to perform the necessary operations."""

__all__ = [
    "EdgeCommunicationHandler",
    "EdgeConnectionDisconnected",
    "EdgeConnectionFailed",
    "EdgeProtocol",
    "EdgeProtocolCallback",
    "MessageHandler",
    "PING",
    "PONG",
]

import inspect
from abc import ABC, abstractmethod
from asyncio import sleep
from typing import Awaitable, Callable, Protocol, runtime_checkable

from loguru import logger

from .messages import CarlosMessage, MessageType
from .types import DeviceId


class EdgeConnectionDisconnected(Exception):
    """Raised when the connection is disconnected."""


class EdgeConnectionFailed(Exception):
    """Raised when the connection attempt fails."""


EdgeProtocolCallback = Callable[["EdgeProtocol"], Awaitable[None]]


class EdgeProtocol(ABC):
    """An abstract protocol that defines the necessary operations to be implemented
    by the server and client."""

    def __init__(self, on_connect: EdgeProtocolCallback | None = None):
        self.on_connect = on_connect

    @abstractmethod
    async def send(self, message: CarlosMessage) -> None:
        """Send data to the other end of the connection.

        :param message: The message to send.
        :raises EdgeConnectionDisconnected: If the connection is disconnected.
        """
        raise NotImplementedError()

    @abstractmethod
    async def receive(self) -> CarlosMessage:
        """Receive data from the other end of the connection.

        :return: The received message.
        :raises EdgeConnectionDisconnected: If the connection is disconnected.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Returns True if the connection is connected."""
        raise NotImplementedError()

    @abstractmethod
    async def connect(self):
        """Connects to the server.

        :raises EdgeConnectionFailed: If the connection attempt fails."""
        raise NotImplementedError()

    @abstractmethod
    async def disconnect(self):
        """Called when the connection is disconnected."""
        raise NotImplementedError()


@runtime_checkable
class MessageHandler(Protocol):

    async def __call__(self, protocol: EdgeProtocol, message: CarlosMessage):
        """Handles the incoming message.

        :param protocol: The protocol to use for communication.
        :param message: The incoming message.
        """
        raise NotImplementedError()


class EdgeCommunicationHandler:
    """Handles the communication between the server and the device."""

    def __init__(self, protocol: EdgeProtocol, device_id: DeviceId):
        """Initializes the communication handler. The default implementation contains
        handlers for the ping and pong messages.

        :param protocol: The protocol to use for communication.
        """
        self.protocol = protocol
        self.device_id = device_id

        self._handlers: dict[MessageType, MessageHandler] = {}
        self._stopped = False

        self.register_handlers(
            {
                MessageType.PING: handle_ping,
                MessageType.PONG: handle_pong,
            }
        )

    def stop(self):
        """Stops the communication handler."""
        self._stopped = True

    def register_handlers(self, handlers: dict[MessageType, MessageHandler]):
        """Registers the given handlers.

        :param handlers: The handlers to register.
        """

        expected_function_params = dict(
            inspect.signature(MessageHandler.__call__).parameters
        )
        expected_function_params.pop("self", None)

        for message_type, handler in handlers.items():
            # instance checks won't work, so we check the signature of the function
            # our self
            handler_params = dict(inspect.signature(handler).parameters)
            handler_params.pop("self", None)

            # remove default parameters
            # They are often used to testing purposes and should not be required
            remove_default_args(handler_params)

            if handler_params != expected_function_params:
                raise TypeError(
                    f"Handler {handler} for message type {message_type} "
                    f"does not have the correct signature."
                )

        self._handlers.update(handlers)

    async def send(self, message: CarlosMessage):
        """Sends the given message.

        :param message: The message to send.
        """

        logger.debug(f"Sending message: {message.message_type}")

        await self.protocol.send(message)

    async def listen(self):
        """Starts listening for incoming messages.

        :raises EdgeConnectionDisconnected: If the connection is disconnected.
        """

        if not self.protocol.is_connected:
            await self.protocol.connect()  # pragma: no cover

        while not self._stopped:
            msg = await self.protocol.receive()
            await self.handle_message(msg)
            await sleep(0.1)

    async def handle_message(self, message: CarlosMessage):
        """Handles the incoming message.

        :param message: The incoming message.
        """

        logger.debug(f"Received message: {message.message_type}")

        if handler := self._handlers.get(message.message_type):
            await handler(protocol=self.protocol, message=message)
            return

        logger.warning(  # pragma: no cover
            f"No handler found for message type: {message.message_type}"
        )


def remove_default_args(handler_params):
    """Little helper function to remove function arguments with default values.

    This kind of smells but, let's roll with it for now.
    """
    default_params = []
    for param in handler_params.values():
        if param.default != inspect.Parameter.empty:
            default_params.append(param.name)  # pragma: no cover
    for default_param in default_params:
        handler_params.pop(default_param, None)  # pragma: no cover


async def handle_ping(protocol: EdgeProtocol, message: CarlosMessage):
    """Handles the incoming ping message by responding with a pong."""
    await protocol.send(CarlosMessage(message_type=MessageType.PONG, payload=None))


async def handle_pong(protocol: EdgeProtocol, message: CarlosMessage):
    """Handles the incoming pong message."""
    logger.debug("Received pong message.")


PING = CarlosMessage(message_type=MessageType.PING, payload=None)
PONG = CarlosMessage(message_type=MessageType.PONG, payload=None)
