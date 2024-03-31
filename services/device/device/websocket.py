"""This module contains the websocket implementation for the device client protocol."""

__all__ = [
    "connect",
    "DeviceWebsocketClient",
]

import websockets
from carlos.edge.interface import CarlosMessage, EdgeProtocol
from carlos.edge.interface.protocol import EdgeConnectionDisconnected

from .connection import ConnectionSettings


async def connect(settings: ConnectionSettings) -> websockets.WebSocketClientProtocol:
    """Connects to the server.

    :param settings: The settings required to make the connection.
    :return: The connection.
    """
    return await websockets.connect(uri=settings.websocket_uri)


class DeviceWebsocketClient(EdgeProtocol):

    def __init__(self, connection: websockets.WebSocketClientProtocol):
        """Initializes the websocket client.

        :param connection: The settings of the websocket connection.
        """
        self._connection = connection

    async def send(self, message: CarlosMessage) -> None:
        """Send data to the other end of the connection.

        :param message: The message to send.
        :raises EdgeConnectionDisconnected: If the connection is disconnected.
        """
        await self._connection.send(message.build())

    async def receive(self) -> CarlosMessage:
        """Receive data from the other end of the connection.

        :return: The received message.
        :raises EdgeConnectionDisconnected: If the connection is disconnected.
        """

        try:
            message = await self._connection.recv()
        except websockets.ConnectionClosed as ex:
            raise EdgeConnectionDisconnected() from ex

        if isinstance(message, bytes):
            message = message.decode()

        return CarlosMessage.from_str(message)
