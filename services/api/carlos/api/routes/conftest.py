import pytest_asyncio
from carlos.database.context import RequestContext
from carlos.database.device import (
    CarlosDeviceDriver,
    CarlosDeviceDriverCreate,
    CarlosDeviceSignalCreate,
    create_device_driver,
    create_device_signals,
    delete_device_driver,
)
from carlos.database.testing.expectations import DeviceId
from carlos.edge.interface.device import DriverDirection
from carlos.edge.interface.units import UnitOfMeasurement


@pytest_asyncio.fixture()
async def driver(async_carlos_db_context: RequestContext):

    device_id = DeviceId.DEVICE_A.value

    to_create = CarlosDeviceDriverCreate(
        display_name="My Driver",
        is_visible_on_dashboard=True,
        driver_identifier="my-driver",
        direction=DriverDirection.INPUT,
        driver_module="does_not_matter",
    )

    created = await create_device_driver(
        context=async_carlos_db_context, device_id=device_id, driver=to_create
    )

    yield created

    # cleanup: delete the driver
    await delete_device_driver(
        context=async_carlos_db_context,
        device_id=device_id,
        driver_identifier=created.driver_identifier,
    )


@pytest_asyncio.fixture()
async def driver_signals(
    async_carlos_db_context: RequestContext, driver: CarlosDeviceDriver
):

    to_create = [
        CarlosDeviceSignalCreate(
            display_name="Temperature",
            unit_of_measurement=UnitOfMeasurement.CELSIUS,
            is_visible_on_dashboard=True,
            signal_identifier="temperature",
        ),
        CarlosDeviceSignalCreate(
            display_name="Humidity",
            unit_of_measurement=UnitOfMeasurement.HUMIDITY_PERCENTAGE,
            is_visible_on_dashboard=True,
            signal_identifier="humidity",
        ),
    ]

    created = await create_device_signals(
        context=async_carlos_db_context,
        device_id=driver.device_id,
        driver_identifier=driver.driver_identifier,
        signals=to_create,
    )

    yield created
