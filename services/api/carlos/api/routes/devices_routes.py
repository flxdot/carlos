__all__ = ["devices_router"]

from uuid import UUID

from carlos.database.context import RequestContext
from carlos.database.device.device_management import (
    CarlosDevice,
    CarlosDeviceCreate,
    CarlosDeviceUpdate,
    create_device,
    get_device,
    list_devices,
    update_device, CarlosDeviceCreate,
)
from fastapi import APIRouter, Depends, Path

from carlos.api.depends.context import request_context

devices_router = APIRouter()


@devices_router.get("", summary="Get all devices.", response_model=list[CarlosDevice])
async def list_devices_route(
    context: RequestContext = Depends(request_context),
):  # pragma: no cover
    """List all devices."""
    return await list_devices(context=context)


@devices_router.post("", summary="Register a new device", response_model=CarlosDevice)
async def register_device_route(
    device: CarlosDeviceCreate,
    context: RequestContext = Depends(request_context),
):  # pragma: no cover
    """Register a new device."""
    return await create_device(context=context, device=device)


DEVICE_ID_PATH: UUID = Path(
    ...,
    title="Device ID",
    description="The unique identifier of the device.",
)


@devices_router.get(
    "/{deviceId}", summary="Get a device by its ID.", response_model=CarlosDevice
)
async def get_device_route(
    device_id: UUID = DEVICE_ID_PATH,
    context: RequestContext = Depends(request_context),
):  # pragma: no cover
    """Get a device by its ID."""
    return await get_device(context=context, device_id=device_id)


@devices_router.put(
    "/{deviceId}", summary="Update a device by its ID.", response_model=CarlosDevice
)
async def update_device_route(
    device: CarlosDeviceUpdate,
    device_id: UUID = DEVICE_ID_PATH,
    context: RequestContext = Depends(request_context),
):  # pragma: no cover
    """Update a device by its ID."""
    return await update_device(context=context, device_id=device_id, device=device)
