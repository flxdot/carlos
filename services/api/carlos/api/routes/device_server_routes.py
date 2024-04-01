"""This module contains the routes used by the carlos edge devices to receive data from
the API."""

__all__ = ["device_server_router"]


from carlos.edge.interface import (
    CarlosMessage,
    EdgeCommunicationHandler,
    EdgeConnectionDisconnected,
    EdgeProtocol,
)
from carlos.edge.interface.endpoint import (
    get_websocket_endpoint,
    get_websocket_token_endpoint,
)
from carlos.edge.server.connection import DeviceConnectionManager
from carlos.edge.server.token import issue_token, verify_token
from fastapi import APIRouter, Path, Query, Request, Security, WebSocket
from jwt import InvalidTokenError
from pydantic.alias_generators import to_camel
from starlette.responses import PlainTextResponse
from starlette.websockets import WebSocketDisconnect, WebSocketState

from carlos.api.depends.authentication import VerifyToken

device_server_router = APIRouter()


DEVICE_ID_ALIAS = to_camel("device_id")
DEVICE_ID_PATH: str = Path(
    ..., alias="deviceId", description="The unique identifier of the device."
)

device_id_param = "{" + DEVICE_ID_ALIAS + "}"

authentication = VerifyToken()


@device_server_router.get(
    get_websocket_token_endpoint(device_id_param),
    summary="Get a token to be used to connect to the websocket.",
    dependencies=[Security(authentication.verify)],
    response_model=str,
    response_class=PlainTextResponse,
)
async def get_device_server_websocket_token(
    request: Request, device_id: str = DEVICE_ID_PATH
):
    """Returns a token that can be used to authenticate the edge device to the API."""
    return issue_token(device_id=device_id, hostname=request.client.host)


device_connection_manager = DeviceConnectionManager()


class WebsocketProtocol(EdgeProtocol):
    """A websocket implementation of the EdgeProtocol."""

    def __init__(self, websocket: WebSocket):
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
            return CarlosMessage.from_str(await self._websocket.receive_text())
        except WebSocketDisconnect as ex:
            raise EdgeConnectionDisconnected(
                f"Connection was closed by the device (code: {ex.code}): {ex.reason}"
            ) from ex

    @property
    def is_connected(self) -> bool:
        """Returns True if the connection is connected."""
        return self._websocket.application_state == WebSocketState.CONNECTED

    async def connect(self):
        """Connects to the server.

        :raises EdgeConnectionFailed: If the connection attempt fails."""
        await self._websocket.accept()

    async def disconnect(self):
        """Called when the connection is disconnected."""
        await self._websocket.close()


@device_server_router.websocket(get_websocket_endpoint(device_id_param))
async def device_server_websocket(
    websocket: WebSocket,
    device_id: str = DEVICE_ID_PATH,
    token: str = Query(..., description="The token to authenticate the device."),
):
    """Handles the connection of the edge server to the API."""

    try:
        token = verify_token(
            token=token, device_id=device_id, hostname=websocket.client.host
        )
    except InvalidTokenError:
        await websocket.close(code=4003, reason="Invalid token.")
        return

    protocol = WebsocketProtocol(websocket)
    await protocol.connect()  # accepts the connection
    await device_connection_manager.connect(protocol)

    try:
        await EdgeCommunicationHandler(protocol=protocol).listen()
    except EdgeConnectionDisconnected:
        device_connection_manager.disconnect(protocol)
