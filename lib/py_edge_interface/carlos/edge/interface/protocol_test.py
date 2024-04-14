import asyncio
import random
from asyncio import Queue
from collections import defaultdict
from threading import Thread
from time import sleep
from typing import Any
from uuid import uuid4

import pytest

from carlos.edge.interface import (
    CarlosMessage,
    EdgeCommunicationHandler,
    EdgeProtocol,
    MessageType,
)

from .plugin_pytest import EdgeProtocolTestingConnection
from .protocol import EdgeConnectionDisconnected, handle_ping, handle_pong


def run_communication_handler(handler: EdgeCommunicationHandler):
    try:
        asyncio.run(handler.listen())
    except EdgeConnectionDisconnected:
        pass


def prepare_handler(
    connection: EdgeProtocolTestingConnection,
) -> tuple[EdgeCommunicationHandler, Thread, defaultdict[Any, int]]:
    """Prepares a communication handler for testing."""
    connection.connect()
    handler = EdgeCommunicationHandler(protocol=connection, device_id=uuid4())

    invocations = defaultdict(int)

    async def server_handle_ping(protocol: EdgeProtocol, message: CarlosMessage):
        invocations[MessageType.PING] += 1
        await handle_ping(protocol=protocol, message=message)

    async def server_handle_pong(protocol: EdgeProtocol, message: CarlosMessage):
        invocations[MessageType.PONG] += 1
        await handle_pong(protocol=protocol, message=message)

    handler.register_handlers(
        {
            MessageType.PING: server_handle_ping,
            MessageType.PONG: server_handle_pong,
        }
    )

    thread = Thread(target=lambda: run_communication_handler(handler))

    return handler, thread, invocations


class TestEdgeCommunicationHandler:
    """Various test for the EdgeCommunicationHandler."""

    @pytest.mark.asyncio
    async def test_integration(
        self,
        edge_testing_protocol: tuple[
            EdgeProtocolTestingConnection, EdgeProtocolTestingConnection
        ],
    ):
        """Tests the basic functionality of the EdgeCommunicationHandler."""
        server_connection, client_connection = edge_testing_protocol

        server, server_thread, server_invocations = prepare_handler(server_connection)
        client, client_thread, client_invocations = prepare_handler(client_connection)

        server_thread.start()
        client_thread.start()

        assert server_invocations[MessageType.PING] == 0
        assert server_invocations[MessageType.PONG] == 0
        assert client_invocations[MessageType.PING] == 0
        assert client_invocations[MessageType.PONG] == 0

        try:

            # Test client invoked pings
            client_pings = random.randint(3, 5)
            for _ in range(client_pings):
                await client.send(
                    CarlosMessage(message_type=MessageType.PING, payload=None)
                )

            # give each thread a chance to process the messages
            sleep(1)

            assert server_invocations[MessageType.PING] == client_pings
            assert client_invocations[MessageType.PONG] == client_pings

            # Test server invoked pings
            server_pings = random.randint(3, 5)
            for _ in range(server_pings):
                await server.send(
                    CarlosMessage(message_type=MessageType.PING, payload=None)
                )

            # give each thread a chance to process the messages
            sleep(1)

            assert client_invocations[MessageType.PING] == server_pings
            assert server_invocations[MessageType.PONG] == server_pings

        finally:
            server.stop()
            client.stop()

            server_connection.disconnect()
            client_connection.disconnect()

            server_thread.join()
            client_thread.join()

    def test_register_handlers_errors(self):
        """This test ensures that the register_handlers method raises the correct
        exceptions in case of invalid handlers."""

        handler = EdgeCommunicationHandler(
            protocol=EdgeProtocolTestingConnection(
                receive_queue=Queue(), send_queue=Queue()
            ),
            device_id=uuid4(),
        )

        def no_args():
            pass

        with pytest.raises(TypeError):
            handler.register_handlers({MessageType.PING: no_args})

        def missing_message_arg(protocol):
            pass

        with pytest.raises(TypeError):
            handler.register_handlers({MessageType.PING: missing_message_arg})

        def missing_protocol_arg(message):
            pass

        with pytest.raises(TypeError):
            handler.register_handlers({MessageType.PING: missing_protocol_arg})

        def too_many_args(protocol, message, extra):
            pass

        with pytest.raises(TypeError):
            handler.register_handlers({MessageType.PING: too_many_args})
