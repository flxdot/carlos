"""This module defines the communication handlers for the device."""

from carlos.edge.interface import (
    CarlosMessage,
    EdgeCommunicationHandler,
    EdgeProtocol,
    EdgeVersionPayload,
    MessageType,
)
from semver import Version

from .constants import VERSION
from .update import update_device


class DeviceCommunicationHandler(EdgeCommunicationHandler):
    """Handles and registers all handlers for the device communication."""

    def __init__(self, protocol: EdgeProtocol):
        """Initializes the communication handler. The default implementation contains
        handlers for the ping and pong messages.

        :param protocol: The protocol to use for communication.
        """
        super().__init__(protocol=protocol)

        self.register_handlers(
            {
                MessageType.EDGE_VERSION: handle_edge_version,
            }
        )


async def handle_edge_version(
    protocol: EdgeProtocol, message: CarlosMessage
):  # pragma: no cover
    """Handles the incoming edge version message.

    This is used to determine if the device needs to be updated. For that the server
    sends the version of the edge device library known to the server. We assume that
    the server is always up-to-date. If the server has a newer version than the device,
    the device will be updated.

    :param protocol: The protocol to use for communication.
    :param message: The incoming message.
    """

    message_payload = EdgeVersionPayload.model_validate(message.payload)

    # we strip the leading 'v' from the version string, as the semver parser does not
    # support it
    server_semver = Version.parse(message_payload.version.strip("v"))
    device_semver = Version.parse(VERSION.strip("v"))

    if server_semver > device_semver:
        update_device()
