from carlos.edge.interface.device import DriverDirection

from carlos.database.context import RequestContext
from carlos.database.device import (
    CarlosDeviceDriverCreate,
    CarlosDeviceDriverUpdate,
    create_device_driver,
    delete_device_driver,
    get_device_drivers,
    update_device_driver,
)
from carlos.database.testing.expectations import DeviceId


async def test_driver_crud(async_carlos_db_context: RequestContext):

    device_id = DeviceId.DEVICE_A.value

    no_drivers = await get_device_drivers(
        context=async_carlos_db_context, device_id=device_id
    )
    assert len(no_drivers) == 0, "No drivers should be present"

    # CREATE ####################################################################

    to_create = CarlosDeviceDriverCreate(
        display_name="My Driver",
        is_visible_on_dashboard=True,
        driver_identifier="my-driver",
        direction=DriverDirection.INPUT,
        driver_module="does_not_matter",
    )

    created = await create_device_driver(
        context=async_carlos_db_context, driver=to_create
    )

    found = await get_device_drivers(
        context=async_carlos_db_context, device_id=device_id
    )
    assert len(found) == 1, "Should have 1 driver"
    assert (
        CarlosDeviceDriverCreate.model_validate(found[0].model_dump()) == created
    ), "Should be the same driver"

    # UPDATE ####################################################################

    to_update = CarlosDeviceDriverUpdate(
        display_name="An updated displayName", is_visible_on_dashboard=False
    )

    updated = await update_device_driver(
        context=async_carlos_db_context,
        device_id=created.device_id,
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
