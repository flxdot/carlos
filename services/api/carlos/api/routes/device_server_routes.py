"""This module contains the routes used by the carlos edge devices to receive data from
the API."""

__all__ = ["device_server_router"]

import secrets
from importlib import metadata

from jwt import InvalidTokenError
from starlette.responses import PlainTextResponse

from carlos.edge.interface import CarlosMessage, EdgeVersionPayload, MessageType
from carlos.edge.interface.endpoint import (
    get_websocket_endpoint,
    get_websocket_token_endpoint,
)
from fastapi import APIRouter, Path, Query, Request, Security, WebSocket
from pydantic.alias_generators import to_camel
from starlette.websockets import WebSocketDisconnect

from carlos.api.depends.authentication import VerifyToken, UnauthorizedException
from carlos.edge.server.token import verify_token, issue_token

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


class EdgeConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await websocket.send_text(
            CarlosMessage(
                message_type=MessageType.EDGE_VERSION,
                payload=EdgeVersionPayload(
                    version=metadata.version("carlos.edge.device")
                ),
            ).build()
        )

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = EdgeConnectionManager()


@device_server_router.websocket(get_websocket_endpoint(device_id_param))
async def device_server_websocket(
    websocket: WebSocket,
    device_id: str = DEVICE_ID_PATH,
    token: str = Query(..., description="The token to authenticate the device."),
):
    """Handles the connection of the edge server to the API."""

    try:
        verify_token(token=token, device_id=device_id, hostname=websocket.client.host)
    except InvalidTokenError:
        raise UnauthorizedException("Invalid token.")

    await manager.connect(websocket)
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
