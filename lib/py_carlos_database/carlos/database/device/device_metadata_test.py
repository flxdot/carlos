import pytest
import pytest_asyncio
from carlos.edge.interface.device import DriverDirection
from carlos.edge.interface.units import PhysicalQuantity, UnitOfMeasurement

from carlos.database.context import RequestContext
from carlos.database.device import (
    CarlosDeviceDriver,
    CarlosDeviceDriverCreate,
    CarlosDeviceDriverUpdate,
    CarlosDeviceSignalCreate,
    CarlosDeviceSignalUpdate,
    create_device_driver,
    create_device_signals,
    delete_device_driver,
    delete_device_signal,
    get_device_drivers,
    get_device_signals,
    update_device_driver,
    update_device_signal,
)
from carlos.database.exceptions import NotFound
from carlos.database.testing.expectations import DeviceId


async def test_driver_crud(async_carlos_db_context: RequestContext):

    device_id = DeviceId.DEVICE_A.value

    no_drivers = await get_device_drivers(
        context=async_carlos_db_context, device_id=device_id
    )
    assert len(no_drivers) == 0, "No drivers should be present"

    with pytest.raises(NotFound):
        await get_device_drivers(
            context=async_carlos_db_context, device_id=DeviceId.UNKNOWN.value
        )

    # CREATE ####################################################################

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

    found = await get_device_drivers(
        context=async_carlos_db_context, device_id=device_id
    )
    assert len(found) == 1, "Should have 1 driver"
    assert (
        CarlosDeviceDriverCreate.model_validate(created.model_dump()) == to_create
    ), "Should be the same driver as to_create"
    assert found[0] == created, "Should be the same driver as created"

    # UPDATE ####################################################################

    to_update = CarlosDeviceDriverUpdate(
        display_name="An updated displayName", is_visible_on_dashboard=False
    )

    updated = await update_device_driver(
        context=async_carlos_db_context,
        device_id=device_id,
        driver_identifier=created.driver_identifier,
        driver=to_update,
    )

    found = await get_device_drivers(
        context=async_carlos_db_context, device_id=device_id
    )

    assert len(found) == 1, "Should have 1 driver"

    assert found[0] == updated, "Should be the same driver"

    assert found[0].display_name == "An updated displayName"
    assert found[0].is_visible_on_dashboard is False
    assert found[0].device_id == created.device_id, "device_id should not change"
    assert (
        found[0].driver_identifier == created.driver_identifier
    ), "driver_identifier should not change"
    assert found[0].direction == created.direction, "direction should not change"
    assert (
        found[0].driver_module == created.driver_module
    ), "driver_module should not change"

    with pytest.raises(NotFound):
        await update_device_driver(
            context=async_carlos_db_context,
            device_id=device_id,
            driver_identifier="non-existent",
            driver=to_update,
        )
    with pytest.raises(NotFound):
        await update_device_driver(
            context=async_carlos_db_context,
            device_id=DeviceId.UNKNOWN.value,
            driver_identifier=created.driver_identifier,
            driver=to_update,
        )

    # DELETE ####################################################################

    await delete_device_driver(
        context=async_carlos_db_context,
        device_id=created.device_id,
        driver_identifier=created.driver_identifier,
    )

    found = await get_device_drivers(
        context=async_carlos_db_context, device_id=device_id
    )
    assert len(found) == 0, "Should have 0 drivers"

    # deleting again should not raise an error
    await delete_device_driver(
        context=async_carlos_db_context,
        device_id=created.device_id,
        driver_identifier=created.driver_identifier,
    )


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

    await delete_device_driver(
        context=async_carlos_db_context,
        device_id=created.device_id,
        driver_identifier=created.driver_identifier,
    )


async def test_driver_signals_crud(
    async_carlos_db_context: RequestContext, driver: CarlosDeviceDriver
):

    no_signals = await get_device_signals(
        context=async_carlos_db_context,
        device_id=driver.device_id,
        driver_identifier=driver.driver_identifier,
    )
    assert len(no_signals) == 0, "No signals should be present"

    with pytest.raises(NotFound):
        await get_device_signals(
            context=async_carlos_db_context,
            device_id=driver.device_id,
            driver_identifier="non-existent",
        )
    with pytest.raises(NotFound):
        await get_device_signals(
            context=async_carlos_db_context,
            device_id=DeviceId.UNKNOWN.value,
            driver_identifier=driver.driver_identifier,
        )

    # CREATE ####################################################################

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

    found = await get_device_signals(
        context=async_carlos_db_context,
        device_id=driver.device_id,
        driver_identifier=driver.driver_identifier,
    )
    assert len(found) == 2, "Should have 2 signals"
    assert sorted(found, key=lambda f: f.timeseries_id) == sorted(
        created, key=lambda c: c.timeseries_id
    ), "Should be the same signals"

    # UPDATE ####################################################################

    timeseries_id = created[0].timeseries_id
    to_update = CarlosDeviceSignalUpdate(
        display_name="Temperature Updated",
        unit_of_measurement=UnitOfMeasurement.FAHRENHEIT,
        is_visible_on_dashboard=False,
    )

    updated = await update_device_signal(
        context=async_carlos_db_context,
        timeseries_id=timeseries_id,
        signal=to_update,
    )

    found = await get_device_signals(
        context=async_carlos_db_context,
        device_id=driver.device_id,
        driver_identifier=driver.driver_identifier,
    )

    assert len(found) == 2, "Should have 2 signals"

    assert updated.display_name == "Temperature Updated"
    assert updated.unit_of_measurement == UnitOfMeasurement.FAHRENHEIT
    assert updated.is_visible_on_dashboard is False
    assert isinstance(updated.physical_quantity, PhysicalQuantity)

    found_map = {f.timeseries_id: f for f in found}

    assert found_map[timeseries_id] == updated, "Should be the same signal"

    with pytest.raises(NotFound):
        await update_device_signal(
            context=async_carlos_db_context,
            timeseries_id=-1,
            signal=to_update,
        )

    # DELETE ####################################################################

    await delete_device_signal(
        context=async_carlos_db_context,
        timeseries_id=created[0].timeseries_id,
    )

    found = await get_device_signals(
        context=async_carlos_db_context,
        device_id=driver.device_id,
        driver_identifier=driver.driver_identifier,
    )
    assert len(found) == 1, "Should have 1 signal"

    # deleting again should not raise an error
    await delete_device_signal(
        context=async_carlos_db_context,
        timeseries_id=created[0].timeseries_id,
    )

    # deliberately don't delete the last signal, as the delete cascade should take
    # of the driver should care of it
