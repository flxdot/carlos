__all__ = ["devices_router"]

from carlos.database.context import RequestContext
from carlos.database.device import (
    CarlosDevice,
    CarlosDeviceCreate,
    CarlosDeviceUpdate,
    create_device,
    get_device,
    list_devices,
    update_device,
)
from fastapi import APIRouter, Depends, Path

from carlos.api.depends.context import request_context
from carlos.edge.interface import DeviceId

devices_router = APIRouter()


@devices_router.get("", summary="Get all devices.", response_model=list[CarlosDevice])
async def list_devices_route(
    context: RequestContext = Depends(request_context),
):
    """List all devices."""
    return await list_devices(context=context)


@devices_router.post("", summary="Register a new device", response_model=CarlosDevice)
async def register_device_route(
    device: CarlosDeviceCreate,
    context: RequestContext = Depends(request_context),
):
    """Register a new device."""
    return await create_device(context=context, device=device)


DEVICE_ID_PATH: DeviceId = Path(
    ...,
    alias="deviceId",
    description="The unique identifier of the device.",
)


@devices_router.get(
    "/{deviceId}", summary="Get a device by its ID.", response_model=CarlosDevice
)
async def get_device_route(
    device_id: DeviceId = DEVICE_ID_PATH,
    context: RequestContext = Depends(request_context),
):
    """Get a device by its ID."""
    return await get_device(context=context, device_id=device_id)


@devices_router.put(
    "/{deviceId}", summary="Update a device by its ID.", response_model=CarlosDevice
)
async def update_device_route(
    device: CarlosDeviceUpdate,
    device_id: DeviceId = DEVICE_ID_PATH,
    context: RequestContext = Depends(request_context),
):
    """Update a device by its ID."""
    return await update_device(context=context, device_id=device_id, device=device)
