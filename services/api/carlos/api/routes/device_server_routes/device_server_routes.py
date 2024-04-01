"""This module contains the routes used by the carlos edge devices to receive data from
the API."""

__all__ = ["device_server_router"]

import warnings

from carlos.edge.interface import EdgeCommunicationHandler, EdgeConnectionDisconnected
from carlos.edge.interface.endpoint import (
    get_websocket_endpoint,
    get_websocket_token_endpoint,
)
from carlos.edge.server.token import issue_token, verify_token
from fastapi import APIRouter, Path, Query, Request, Security, WebSocket
from jwt import InvalidTokenError
from pydantic.alias_generators import to_camel
from starlette.responses import PlainTextResponse

from carlos.api.depends.authentication import VerifyToken

from .protocol import WebsocketProtocol
from .state import DEVICE_CONNECTION_MANAGER

device_server_router = APIRouter()


DEVICE_ID_ALIAS = to_camel("device_id")
DEVICE_ID_PATH: str = Path(
    ..., alias="deviceId", description="The unique identifier of the device."
)
device_id_param = "{" + DEVICE_ID_ALIAS + "}"

AUTHENTICATION = VerifyToken()


def extract_client_hostname(connection: Request | WebSocket) -> str:
    """Extracts the hostname of the client from the request."""

    if connection.client is None:
        warnings.warn("The client hostname is unknown.")
        return "unknown"
    # The test client has no host connected, thus we can never cover this line during
    # testing
    return connection.client.host  # pragma: no cover


@device_server_router.get(
    get_websocket_token_endpoint(device_id_param),
    summary="Get a token to be used to connect to the websocket.",
    dependencies=[Security(AUTHENTICATION.verify)],
    response_model=str,
    response_class=PlainTextResponse,
)
async def get_device_server_websocket_token(
    request: Request, device_id: str = DEVICE_ID_PATH
):
    """Returns a token that can be used to authenticate the edge device to the API."""

    return issue_token(device_id=device_id, hostname=extract_client_hostname(request))


@device_server_router.websocket(get_websocket_endpoint(device_id_param))
async def device_server_websocket(
    websocket: WebSocket,
    device_id: str = DEVICE_ID_PATH,
    token: str = Query(..., description="The token to authenticate the device."),
):
    """Handles the connection of the edge server to the API."""

    try:
        token = verify_token(
            token=token,
            device_id=device_id,
            hostname=extract_client_hostname(websocket),
        )
    except InvalidTokenError:
        await websocket.close(code=4003, reason="Invalid token.")
        return

    protocol = WebsocketProtocol(websocket)
    await protocol.connect()  # accepts the connection
    await DEVICE_CONNECTION_MANAGER.add_device(device_id=device_id, protocol=protocol)

    try:
        await EdgeCommunicationHandler(protocol=protocol).listen()
    except EdgeConnectionDisconnected:
        DEVICE_CONNECTION_MANAGER.remove(device_id)
