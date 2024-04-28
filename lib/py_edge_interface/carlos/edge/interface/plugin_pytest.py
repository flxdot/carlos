__all__ = ["EdgeProtocolTestingConnection"]

from asyncio import Queue, QueueEmpty, sleep

import pytest

from carlos.edge.interface import CarlosMessage, EdgeProtocol
from carlos.edge.interface.protocol import (
    EdgeConnectionDisconnected,
    EdgeProtocolCallback,
)


class EdgeProtocolTestingConnection(EdgeProtocol):
    """The EdgeTestProtocol is a very simple implementation of the EdgeProtocol
    utilizing an async FIFO queue to simulate the communication between the server
    and the client. This is useful for testing purposes."""

    def __init__(
        self,
        send_queue: Queue[str],
        receive_queue: Queue[str],
        on_connect: EdgeProtocolCallback | None = None,
    ):

        super().__init__(on_connect=on_connect)

        self._send_queue = send_queue
        self._receive_queue = receive_queue

        self._is_connected = True

    @property
    def is_connected(self) -> bool:
        """Returns whether the connection is connected or not."""
        return self._is_connected  # pragma: no cover

    def disconnect(self):
        """Set the connection to disconnected. This will allow the receive method to
        return at some point."""
        self._is_connected = False

    def connect(self):
        """Set the connection to connected. This will allow the receive method to
        return at some point.

        :raises EdgeConnectionFailed: If the connection attempt fails."""
        self._is_connected = True

        if self.on_connect:
            self.on_connect(self)  # pragma: no cover

    async def send(self, message: CarlosMessage) -> None:
        """Send data to the other end of the connection.

        :param message: The message to send.
        """
        await self._send_queue.put(message.build())

    async def receive(self) -> CarlosMessage:
        """Receive data from the other end of the connection.

        :return: The received message.
        """

        # In order to allow the test finish at some point we need a means to stop the
        # reading. This is done by disconnecting the connection.
        while self._is_connected:
            try:
                message = self._receive_queue.get_nowait()
            except QueueEmpty:
                await sleep(0.1)
                continue
            return CarlosMessage.from_str(message)

        raise EdgeConnectionDisconnected("Connection was disconnected.")


@pytest.fixture(name="edge_testing_protocol")
def fixture_edge_testing_protocol() -> (
    tuple[EdgeProtocolTestingConnection, EdgeProtocolTestingConnection]
):
    """Fixture that returns a server and client instance of the EdgeTestProtocol.

    :return: A tuple with the server and client protocol.
    """

    server_queue: Queue[str] = Queue()
    client_queue: Queue[str] = Queue()

    server = EdgeProtocolTestingConnection(
        send_queue=server_queue, receive_queue=client_queue
    )
    client = EdgeProtocolTestingConnection(
        send_queue=client_queue, receive_queue=server_queue
    )

    return server, client
