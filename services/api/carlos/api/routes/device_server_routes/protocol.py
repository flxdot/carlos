__all__ = ["WebsocketProtocol"]

from carlos.edge.interface import (
    CarlosMessage,
    EdgeConnectionDisconnected,
    EdgeProtocol,
)
from carlos.edge.interface.protocol import EdgeProtocolCallback
from starlette.websockets import WebSocket, WebSocketDisconnect, WebSocketState


class WebsocketProtocol(EdgeProtocol):
    """A websocket implementation of the EdgeProtocol."""

    def __init__(
        self, websocket: WebSocket, on_connect: EdgeProtocolCallback | None = None
    ):

        super().__init__(on_connect=on_connect)

        self._websocket = websocket

    async def send(self, message: CarlosMessage) -> None:
        """Send data to the other end of the connection.

        :param message: The message to send.
        :raises EdgeConnectionDisconnected: If the connection is disconnected.
        """
        await self._websocket.send_text(message.build())

    async def receive(self) -> CarlosMessage:
        """Receive data from the other end of the connection.

        :return: The received message.
        :raises EdgeConnectionDisconnected: If the connection is disconnected.
        """
        try:
            raw_message = await self._websocket.receive_text()
        except WebSocketDisconnect as ex:
            raise EdgeConnectionDisconnected(
                f"Connection was closed by the device (code: {ex.code}): {ex.reason}"
            ) from ex

        return CarlosMessage.from_str(raw_message)

    @property
    def is_connected(self) -> bool:
        """Returns True if the connection is connected."""
        return self._websocket.application_state == WebSocketState.CONNECTED

    async def connect(self):
        """Connects to the server.

        :raises EdgeConnectionFailed: If the connection attempt fails."""
        await self._websocket.accept()

        if self.on_connect and self.is_connected:
            await self.on_connect(self)

    async def disconnect(self):  # pragma: no cover
        """Called when the connection is disconnected."""
        if self.is_connected:
            await self._websocket.close()
