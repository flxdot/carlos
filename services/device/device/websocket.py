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

    def __init__(self, settings: ConnectionSettings):
        """Initializes the websocket client.

        :param settings: The settings of the websocket connection.
        """
        self._settings = settings

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

        logger.info(f"Connected to the server: {self._settings.server_url}")

    async def _do_connect(self) -> websockets.WebSocketClientProtocol:
        """Internal method to perform the connection to the websocket."""

        async with AsyncClient() as client:
            auth0_token = await self._get_auth0_token(client=client)
            token = await self.get_websocket_token(
                client=client, auth0_token=auth0_token
            )

        websocket_uri = self._settings.get_websocket_uri(
            device_id=self._settings.device_id, token=token
        )

        return await websockets.connect(websocket_uri)

    async def get_websocket_token(self, client: AsyncClient, auth0_token: str) -> str:
        """Fetches a new websocket token from the API.

        The auth0 token is required to authenticate with the API.

        :param client: The HTTP client to use.
        :param auth0_token: The Auth0 token to use.
        :return: The websocket token.
        :raises ConnectionError: If the token could not be fetched.
        """

        response = await client.get(
            self._settings.get_websocket_token_uri(device_id=self._settings.device_id),
            headers={"Authorization": f"Bearer {auth0_token}"},
        )
        if not response.is_success:
            raise ConnectionError("Failed to get the token.")
        token = response.text
        return token

    async def _get_auth0_token(self, client: AsyncClient) -> str:
        """Fetches an Auth0 token.

        :param client: The HTTP client to use.
        :return: The Auth0 token to be used to authenticate with the Carlos API.
        :raises ConnectionError: If the token could not be fetched.
        """

        auth0_response = await client.post(
            f"https://{self._settings.auth0.domain}/oauth/token",
            json={
                "audience": self._settings.auth0.audience,
                "client_id": self._settings.auth0.client_id,
                "client_secret": self._settings.auth0.client_secret,
                "grant_type": "client_credentials",
            },
        )
        if not auth0_response.is_success:
            raise ConnectionError("Failed to authenticate with Auth0.")
        return auth0_response.json()["access_token"]

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
