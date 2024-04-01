from importlib import metadata

from carlos.edge.interface import (
    CarlosMessage,
    EdgeProtocol,
    EdgeVersionPayload,
    MessageType,
)


class DeviceConnectionManager:
    """This class manages all active connections to any connected devices."""

    def __init__(self):
        self._active_connections: dict[str, EdgeProtocol] = {}

    @property
    def connected_devices(self) -> list[str]:
        """Returns a list of all connected devices."""

        return list(self._active_connections.keys())

    async def add_device(self, device_id: str, protocol: EdgeProtocol):
        """Adds the given protocol to the active connections and sends
        the handshake messages.

        :param device_id: The unique identifier of the device.
        :param protocol: The corresponding protocol of the device.
        """

        # if a device with the same id is already connected, disconnect it
        if device_id in self._active_connections:  # pragma: no cover
            await self._active_connections[device_id].disconnect()
        self._active_connections[device_id] = protocol

        # After a successful connection, we need to send a series of messages
        await protocol.send(
            CarlosMessage(
                message_type=MessageType.EDGE_VERSION,
                payload=EdgeVersionPayload(
                    version=metadata.version("carlos.edge.device")
                ),
            )
        )

    def remove(self, device_id: str):
        """Removes the given protocol from the active connections."""

        self._active_connections.pop(device_id, None)

    @staticmethod
    async def send(message: CarlosMessage, protocol: EdgeProtocol):
        """Sends the given message via the given protocol."""

        await protocol.send(message)

    async def broadcast(self, message: CarlosMessage):
        """Sends the given message to all active connections."""

        for connection in self._active_connections.values():
            await connection.send(message)
