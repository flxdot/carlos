from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from carlos.database.utils import utcnow

from ..context import RequestContext
from ..exceptions import NotFound
from .device_management import (
    CarlosDevice,
    CarlosDeviceCreate,
    CarlosDeviceUpdate,
    create_device,
    get_device,
    list_devices,
    set_device_seen,
    update_device,
)


class TestCarlosDevice:

    @pytest.mark.parametrize(
        "last_seen_at, expected_online",
        [
            pytest.param(None, False, id="Never seen"),
            pytest.param(utcnow(), True, id="seen now"),
            pytest.param(utcnow() - timedelta(days=1), False, id="seen yesterday"),
        ],
    )
    def test_is_online(self, last_seen_at: datetime | None, expected_online: bool):
        """This test ensures that the `is_online` property returns the correct
        results."""
        device = CarlosDevice(
            last_seen_at=last_seen_at,
            display_name="does not matter",
            device_id=uuid4(),
            registered_at=utcnow(),
        )
        assert device.is_online is expected_online


@pytest.mark.asyncio()
async def test_device_crud(async_carlos_db_context: RequestContext):
    """This method ensures that the CRUD functionality of the device management
    works as expected."""

    # A unknown device should raise a NotFound exception.
    with pytest.raises(NotFound):
        await get_device(context=async_carlos_db_context, device_id=uuid4())

    no_devices = await list_devices(context=async_carlos_db_context)
    assert len(no_devices) == 0

    # Create a new device.
    created = await create_device(
        context=async_carlos_db_context,
        device=CarlosDeviceCreate(
            display_name="Test Device", description="Test Description"
        ),
    )
    fetched = await get_device(
        context=async_carlos_db_context,
        device_id=created.device_id,
    )
    assert fetched == created

    # Update the device.
    updated = await update_device(
        context=async_carlos_db_context,
        device_id=created.device_id,
        device=CarlosDeviceUpdate(
            display_name="Test Device (updated)",
            description="Test Description (updated)",
        ),
    )
    assert updated.display_name == "Test Device (updated)"
    assert updated.description == "Test Description (updated)"

    # Ensure that we can't update an unknown device.
    with pytest.raises(NotFound):
        await update_device(
            context=async_carlos_db_context,
            device_id=uuid4(),
            device=CarlosDeviceUpdate(
                display_name="Test Device (updated)",
                description="Test Description (updated)",
            ),
        )

    at_least_one = await list_devices(context=async_carlos_db_context)
    assert len(at_least_one) == len(no_devices) + 1


@pytest.mark.asyncio()
async def test_set_device_seen(async_carlos_db_context: RequestContext):
    """This test ensures that the `set_device_seen` method works as expected."""
    device = await create_device(
        context=async_carlos_db_context,
        device=CarlosDeviceCreate(
            display_name="Test Device", description="Test Description"
        ),
    )

    # Ensure that the device is not seen.
    assert device.last_seen_at is None

    # Update the last seen timestamp.
    await set_device_seen(context=async_carlos_db_context, device_id=device.device_id)

    # Ensure that the device is seen.
    updated = await get_device(
        context=async_carlos_db_context, device_id=device.device_id
    )
    assert updated.last_seen_at is not None
    assert updated.last_seen_at > device.registered_at
    assert (updated.last_seen_at - utcnow()) <= timedelta(seconds=1)
