"""This module defines the communication handlers for the device."""

from carlos.edge.interface import (
    CarlosMessage,
    DeviceId,
    EdgeCommunicationHandler,
    EdgeConnectionDisconnected,
    EdgeProtocol,
    EdgeVersionPayload,
    MessageType,
)
from loguru import logger
from semver import Version

from .constants import VERSION
from .update import update_device


class ClientEdgeCommunicationHandler(EdgeCommunicationHandler):
    """Handles and registers all handlers for the device communication."""

    def __init__(self, protocol: EdgeProtocol, device_id: DeviceId):
        """Initializes the communication handler. The default implementation contains
        handlers for the ping and pong messages.

        :param protocol: The protocol to use for communication.
        """
        super().__init__(protocol=protocol, device_id=device_id)

        self.register_handlers(
            {
                MessageType.EDGE_VERSION: handle_edge_version,
            }
        )

    async def listen(self):  # pragma: no cover
        """The client specific implementation of the listen method should always
        try to reconnect if the connection is lost."""

        while not self._stopped:
            try:
                await super().listen()
            except EdgeConnectionDisconnected:
                await self.protocol.connect()


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
        logger.info(
            f"Device version is outdated. Updating device to version {server_semver}.",
        )
        update_device()
    else:
        logger.info(f"Device version ({device_semver}) is up-to-date.")
