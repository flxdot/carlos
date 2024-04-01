"""This module contains the websocket implementation for the device client protocol."""

__all__ = [
    "DeviceWebsocketClient",
]


import websockets
from carlos.edge.device.retry import BackOff
from carlos.edge.interface import CarlosMessage, EdgeProtocol
from carlos.edge.interface.protocol import EdgeConnectionDisconnected
from httpx import AsyncClient
from loguru import logger

from .connection import ConnectionSettings


# can only be tested in integration tests
class DeviceWebsocketClient(EdgeProtocol):  # pragma: no cover

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

        connection_strategy = BackOff()
        self._connection = await connection_strategy.execute(
            func=self._do_connect, expected_exceptions=(Exception,)
        )

        logger.info(f"Connected to the server: {self._settings.server_host}")

    async def _do_connect(self) -> websockets.WebSocketClientProtocol:
        """Internal method to perform the connection to the websocket."""

        async with AsyncClient() as client:
            response = await client.get(
                self._settings.get_websocket_token_uri(device_id=self._device_id)
            )
            token = response.text

        websocket_uri = self._settings.get_websocket_uri(
            device_id=self._device_id, token=token
        )

        return await websockets.connect(websocket_uri)

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

        # we can guarantee that the connection is not None
        await self._connection.send(message.build())  # type: ignore[union-attr]

    async def receive(self) -> CarlosMessage:
        """Receive data from the other end of the connection.

        :return: The received message.
        :raises EdgeConnectionDisconnected: If the connection is disconnected.
        """

        if not self.is_connected:
            raise EdgeConnectionDisconnected("The connection is not connected.")

        try:
            # we can guarantee that the connection is not None
            message = await self._connection.recv()  # type: ignore[union-attr]
        except websockets.ConnectionClosed as ex:
            raise EdgeConnectionDisconnected() from ex

        if isinstance(message, bytes):
            message = message.decode()

        return CarlosMessage.from_str(message)
