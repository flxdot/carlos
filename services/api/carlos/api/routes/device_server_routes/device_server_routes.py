"""This module contains the routes used by the carlos edge devices to receive data from
the API."""

__all__ = ["device_server_router"]

import warnings

from carlos.database.context import RequestContext
from carlos.database.device import ensure_device_exists, set_device_seen
from carlos.database.exceptions import NotFound
from carlos.edge.interface import DeviceId, EdgeConnectionDisconnected
from carlos.edge.interface.endpoint import (
    get_websocket_endpoint,
    get_websocket_token_endpoint,
)
from carlos.edge.server.device_handler import ServerDeviceCommunicationHandler
from carlos.edge.server.token import issue_token, verify_token
from fastapi import APIRouter, Depends, Query, Request, Security, WebSocket
from jwt import InvalidTokenError
from pydantic.alias_generators import to_camel
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.responses import PlainTextResponse

from carlos.api.depends.authentication import verify_token as auth_verify_token
from carlos.api.depends.context import request_context
from carlos.api.routes.devices_routes import DEVICE_ID_PATH

from ...depends.database import carlos_db_connection
from .protocol import WebsocketProtocol
from .state import DEVICE_CONNECTION_MANAGER

device_server_router = APIRouter()


DEVICE_ID_ALIAS = to_camel("device_id")
device_id_param = "{" + DEVICE_ID_ALIAS + "}"


def extract_client_hostname(connection: Request | WebSocket) -> str:
    """Extracts the hostname of the client from the request."""

    if connection.client is None:  # pragma: no cover
        warnings.warn("The client hostname is unknown.")
        return "unknown"
    # The test client has no host connected, thus we can never cover this line during
    # testing
    return connection.client.host  # pragma: no cover


@device_server_router.get(
    get_websocket_token_endpoint(device_id_param),
    summary="Get a token to be used to connect to the websocket.",
    dependencies=[Security(auth_verify_token)],
    response_model=str,
    response_class=PlainTextResponse,
    tags=["devices"],
)
async def get_device_server_websocket_token(
    request: Request,
    device_id: DeviceId = DEVICE_ID_PATH,
    context: RequestContext = Depends(request_context),
):
    """Returns a token that can be used to authenticate the edge device to the API."""

    await ensure_device_exists(context=context, device_id=device_id)

    return issue_token(device_id=device_id, hostname=extract_client_hostname(request))


@device_server_router.websocket(get_websocket_endpoint(device_id_param))
async def device_server_websocket(
    websocket: WebSocket,
    device_id: DeviceId = DEVICE_ID_PATH,
    token: str = Query(..., description="The token to authenticate the device."),
    connection: AsyncConnection = Depends(carlos_db_connection),
):
    """Handles the connection of the edge server to the API."""

    context = RequestContext(connection=connection)

    try:
        await ensure_device_exists(context=context, device_id=device_id)
    except NotFound:
        await websocket.close(code=4004, reason="Unknown device.")
        return

    try:
        verify_token(
            token=token,
            device_id=device_id,
            hostname=extract_client_hostname(websocket),
        )
    except InvalidTokenError:
        await websocket.close(code=4003, reason="Invalid token.")
        return

    await set_device_seen(context=context, device_id=device_id)

    protocol = WebsocketProtocol(websocket)
    await protocol.connect()  # accepts the connection
    await DEVICE_CONNECTION_MANAGER.add_device(device_id=device_id, protocol=protocol)

    try:
        await ServerDeviceCommunicationHandler(
            protocol=protocol, device_id=device_id
        ).listen()
    except EdgeConnectionDisconnected:
        DEVICE_CONNECTION_MANAGER.remove(device_id)
