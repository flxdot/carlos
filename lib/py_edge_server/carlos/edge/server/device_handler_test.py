import pytest
from carlos.database.context import RequestContext
from carlos.database.device import get_device
from carlos.database.testing.expectations import DeviceId
from carlos.edge.interface import CarlosMessage, MessageType
from carlos.edge.interface.plugin_pytest import EdgeProtocolTestingConnection

from .device_handler import ServerEdgeCommunicationHandler


@pytest.fixture()
def device_a_handler(
    edge_testing_protocol: tuple[
        EdgeProtocolTestingConnection, EdgeProtocolTestingConnection
    ]
):

    server, client = edge_testing_protocol

    return ServerEdgeCommunicationHandler(
        protocol=server, device_id=DeviceId.DEVICE_A.value
    )


@pytest.mark.asyncio()
async def test_handle_message(
    device_a_handler: ServerEdgeCommunicationHandler,
    async_carlos_db_context: RequestContext,
):
    """This method tests the effects of the handle_message method."""

    ping = CarlosMessage(message_type=MessageType.PING, payload=None)

    device_a_before = await get_device(
        context=async_carlos_db_context, device_id=DeviceId.DEVICE_A.value
    )

    await device_a_handler.handle_message(ping)

    device_a_after = await get_device(
        context=async_carlos_db_context, device_id=DeviceId.DEVICE_A.value
    )

    # On the first call the last_seen_at might be None, thus we only check for changes.
    # Further down will ensure that the last_seen_at increases.
    assert (
        device_a_before.last_seen_at != device_a_after.last_seen_at
    ), "Last seen was not updated."

    await device_a_handler.handle_message(ping)

    device_a_after_second = await get_device(
        context=async_carlos_db_context, device_id=DeviceId.DEVICE_A.value
    )

    assert (
        device_a_after_second.last_seen_at > device_a_after.last_seen_at
    ), "Last seen did not increase."
