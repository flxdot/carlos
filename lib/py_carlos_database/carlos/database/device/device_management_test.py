from contextlib import nullcontext
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest

from carlos.database.utils import utcnow

from ..context import RequestContext
from ..exceptions import NotFound
from ..testing.expectations import EXPECTED_DEVICE_COUNT, DeviceId
from .device_management import (
    CarlosDevice,
    CarlosDeviceCreate,
    CarlosDeviceUpdate,
    create_device,
    does_device_exist,
    ensure_device_exists,
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

    default_test_devices = await list_devices(context=async_carlos_db_context)
    assert len(default_test_devices) == EXPECTED_DEVICE_COUNT

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
    assert len(at_least_one) == len(default_test_devices) + 1


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


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "device_id, expected_result",
    [
        pytest.param(DeviceId.ONLINE.value, True, id="Online device"),
        pytest.param(DeviceId.UNKNOWN.value, False, id="Unknown device"),
    ],
)
async def test_does_device_exist(
    async_carlos_db_context: RequestContext, device_id: UUID, expected_result: bool
):
    """This test ensures that the `does_device_exist` method works as expected."""

    assert (
        await does_device_exist(context=async_carlos_db_context, device_id=device_id)
        is expected_result
    )


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "device_id, expected_result",
    [
        pytest.param(DeviceId.ONLINE.value, None, id="Online device"),
        pytest.param(DeviceId.UNKNOWN.value, NotFound, id="Unknown device"),
    ],
)
async def test_ensure_device_exists(
    async_carlos_db_context: RequestContext,
    device_id: UUID,
    expected_result: type[Exception] | None,
):
    """This test ensures that the `does_device_exist` method works as expected."""

    if expected_result is None:
        context = nullcontext()
    else:
        context = pytest.raises(expected_result)

    with context:
        await ensure_device_exists(context=async_carlos_db_context, device_id=device_id)
