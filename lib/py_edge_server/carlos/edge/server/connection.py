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
        self.active_connections: list[EdgeProtocol] = []

    async def connect(self, protocol: EdgeProtocol):
        """Adds the given protocol to the active connections and sends
        the handshake messages."""
        self.active_connections.append(protocol)

        # After a successful connection, we need to send a series of messages
        await protocol.send(
            CarlosMessage(
                message_type=MessageType.EDGE_VERSION,
                payload=EdgeVersionPayload(
                    version=metadata.version("carlos.edge.device")
                ),
            )
        )

    def disconnect(self, protocol: EdgeProtocol):
        """Removes the given protocol from the active connections."""
        self.active_connections.remove(protocol)

    @staticmethod
    async def send(message: CarlosMessage, protocol: EdgeProtocol):
        """Sends the given message via the given protocol."""
        await protocol.send(message)

    async def broadcast(self, message: CarlosMessage):
        """Sends the given message to all active connections."""
        for connection in self.active_connections:
            await connection.send(message)
