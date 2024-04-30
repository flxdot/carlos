"""This module defines the communication handlers for the device."""

from collections import defaultdict
from typing import DefaultDict

from carlos.edge.interface import (
    CarlosMessage,
    DeviceId,
    EdgeCommunicationHandler,
    EdgeConnectionDisconnected,
    EdgeProtocol,
    EdgeVersionPayload,
    MessageType,
)
from carlos.edge.interface.messages import DeviceConfigResponsePayload
from loguru import logger
from semver import Version

from .constants import VERSION
from .storage.connection import get_async_storage_engine
from .storage.exceptions import NotFoundError
from .storage.timeseries_index import find_timeseries_index, update_timeseries_index
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
                MessageType.DEVICE_CONFIG_RESPONSE: handle_device_config_response,
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


async def handle_device_config_response(
    protocol: EdgeProtocol, message: CarlosMessage, url: str | None = None
):
    """Handles the incoming device config response message.

    This message is sent by the server as a response to a DEVICE_CONFIG message. It
    contains the timeseries ids for each driver and signal.

    :param protocol: The protocol to use for communication.
    :param message: The incoming message.
    :param url: Optional URL for testing purposes.
    """

    device_config_response = DeviceConfigResponsePayload.model_validate(message.payload)

    async with get_async_storage_engine(url=url).connect() as connection:
        timeseries = await find_timeseries_index(
            connection=connection,
        )
        timeseries_index: DefaultDict[str, dict[str, int]] = defaultdict(dict)
        for ts in timeseries:
            timeseries_index[ts.driver_identifier][ts.driver_signal] = ts.timeseries_id

        for (
            driver_identifier,
            signal_index,
        ) in device_config_response.timeseries_index.items():
            for signal_identifier, timeseries_id in signal_index.items():
                try:
                    await update_timeseries_index(
                        connection=connection,
                        timeseries_id=timeseries_index[driver_identifier][
                            signal_identifier
                        ],
                        server_timeseries_id=timeseries_id,
                    )
                except NotFoundError:  # pragma: no cover
                    logger.exception(
                        f"Error updating timeseries index for {driver_identifier=} and"
                        f" {signal_identifier=}."
                    )
