import pytest
from carlos.database.context import RequestContext
from carlos.database.device import (
    delete_device_driver,
    get_device,
    get_device_drivers,
    get_device_signals,
)
from carlos.database.testing.expectations import DeviceId
from carlos.edge.interface import CarlosMessage, DeviceConfigPayload, MessageType
from carlos.edge.interface.device.driver_config import (
    DriverDirection,
    DriverMetadata,
    DriverSignal,
)
from carlos.edge.interface.plugin_pytest import EdgeProtocolTestingConnection

from ..interface.units import UnitOfMeasurement
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


async def test_handle_device_config(
    device_a_handler: ServerEdgeCommunicationHandler,
    async_carlos_db_context: RequestContext,
):
    """This method tests the effects of the handle_device_config method."""

    device_id = DeviceId.DEVICE_A.value

    drivers = await get_device_drivers(
        context=async_carlos_db_context, device_id=device_id
    )
    assert len(drivers) == 0, "There should be no drivers before we start the test."

    message = CarlosMessage(
        message_type=MessageType.DEVICE_CONFIG,
        payload=DeviceConfigPayload(
            drivers=[
                DriverMetadata(
                    direction=DriverDirection.INPUT,
                    identifier="some-input",
                    driver_module=__package__,
                    signals=[
                        DriverSignal(
                            signal_identifier="signal-1",
                            unit_of_measurement=UnitOfMeasurement.CELSIUS,
                        ),
                        DriverSignal(
                            signal_identifier="signal-2",
                            unit_of_measurement=UnitOfMeasurement.PERCENTAGE,
                        ),
                    ],
                ),
                DriverMetadata(
                    direction=DriverDirection.OUTPUT,
                    identifier="some-output",
                    driver_module=__package__,
                    signals=[
                        DriverSignal(
                            signal_identifier="signal-out",
                            unit_of_measurement=UnitOfMeasurement.UNIT_LESS,
                        ),
                    ],
                ),
            ]
        ),
    )

    await device_a_handler.handle_message(message)

    # Check if the drivers and signals were created.
    drivers = await get_device_drivers(
        context=async_carlos_db_context, device_id=device_id
    )

    assert len(drivers) == 2, "The number of drivers is not correct."

    input_signals = await get_device_signals(
        context=async_carlos_db_context,
        device_id=device_id,
        driver_identifier=message.payload.drivers[0].identifier,
    )
    assert len(input_signals) == 2, "The number of input signals is not correct."

    output_signals = await get_device_signals(
        context=async_carlos_db_context,
        device_id=device_id,
        driver_identifier=message.payload.drivers[1].identifier,
    )
    assert len(output_signals) == 1, "The number of output signals is not correct."

    # cleanup
    for driver in drivers:
        await delete_device_driver(
            context=async_carlos_db_context,
            device_id=driver.device_id,
            driver_identifier=driver.driver_identifier,
        )
