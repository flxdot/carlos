"""This module contains the websocket implementation for the device client protocol."""

__all__ = [
    "DeviceWebsocketClient",
]

import urllib.parse as urlparse
from functools import partial
from urllib.parse import urlencode

import websockets
from carlos.edge.device.retry import BackOff
from carlos.edge.interface import CarlosMessage, EdgeProtocol
from carlos.edge.interface.protocol import EdgeConnectionDisconnected
from httpx import AsyncClient
from loguru import logger

from .connection import ConnectionSettings


class DeviceWebsocketClient(EdgeProtocol):

    def __init__(self, settings: ConnectionSettings, device_id: str):
        """Initializes the websocket client.

        :param settings: The settings of the websocket connection.
        """
        self._settings = settings
        self._device_id = device_id

        self._connection: websockets.WebSocketClientProtocol | None = None

    @property
    def is_connected(self) -> bool:
        """Returns True if the connection is connected."""
        return self._connection is not None and not self._connection.closed

    async def connect(self):
        """Connects to the server.

        :raises EdgeConnectionFailed: If the connection attempt fails."""

        if self.is_connected:
            return

        async with AsyncClient() as client:
            response = await client.get(
                self._settings.get_websocket_token_uri(device_id=self._device_id)
            )
            token = response.text

        url_parts = list(
            urlparse.urlparse(
                self._settings.get_websocket_uri(device_id=self._device_id)
            )
        )
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update({"token": token})
        url_parts[4] = urlencode(query)
        websocket_uri = urlparse.urlunparse(url_parts)

        connection_fcn = partial(websockets.connect, uri=websocket_uri)

        connection_strategy = BackOff()
        self._connection = await connection_strategy.execute(
            func=connection_fcn, expected_exceptions=(Exception,)
        )

        logger.info(f"Connected to the server: {websocket_uri}")

    async def disconnect(self):
        """Called when the connection is disconnected."""
        if self.is_connected:
            await self._connection.close()
            self._connection = None

    async def send(self, message: CarlosMessage) -> None:
        """Send data to the other end of the connection.

        :param message: The message to send.
        :raises EdgeConnectionDisconnected: If the connection is disconnected.
        """

        if not self.is_connected:
            raise EdgeConnectionDisconnected("The connection is not connected.")

        await self._connection.send(message.build())

    async def receive(self) -> CarlosMessage:
        """Receive data from the other end of the connection.

        :return: The received message.
        :raises EdgeConnectionDisconnected: If the connection is disconnected.
        """

        if not self.is_connected:
            raise EdgeConnectionDisconnected("The connection is not connected.")

        try:
            message = await self._connection.recv()
        except websockets.ConnectionClosed as ex:
            raise EdgeConnectionDisconnected() from ex

        if isinstance(message, bytes):
            message = message.decode()

        return CarlosMessage.from_str(message)
