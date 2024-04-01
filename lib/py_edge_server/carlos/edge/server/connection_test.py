import pytest
from carlos.edge.interface import CarlosMessage, MessageType
from carlos.edge.interface.plugin_pytest import EdgeProtocolTestingConnection

from .connection import DeviceConnectionManager


@pytest.mark.asyncio
async def test_device_connection_manager(
    edge_testing_protocol: tuple[
        EdgeProtocolTestingConnection, EdgeProtocolTestingConnection
    ]
):
    """This test ensures that the connection manager works as expected."""

    # this is actual server and client, but for the purpose of this test, we can assume
    # both are clients
    client_a, client_b = edge_testing_protocol

    connection_manager = DeviceConnectionManager()

    # connect the clients
    assert len(connection_manager.active_connections) == 0
    await connection_manager.connect(client_a)
    await connection_manager.connect(client_b)
    assert len(connection_manager.active_connections) == 2

    # we need to ignore the handshake messages
    for _ in range(1):
        await client_a.receive()
        await client_b.receive()

    # broadcast a message
    await connection_manager.broadcast(
        CarlosMessage(message_type=MessageType.PONG, payload=None)
    )
    message_a = await client_a.receive()
    assert message_a.message_type == MessageType.PONG
    message_b = await client_b.receive()
    assert message_b.message_type == MessageType.PONG

    # send a message to client_a
    await connection_manager.send(
        message=CarlosMessage(message_type=MessageType.PING, payload=None),
        protocol=client_b,
    )
    message_a = await client_a.receive()
    assert message_a.message_type == MessageType.PING

    # disconnect client_a
    connection_manager.disconnect(client_a)
    assert len(connection_manager.active_connections) == 1
