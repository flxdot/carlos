__all__ = ["devices_router"]

from carlos.database.context import RequestContext
from carlos.database.device import (
    CarlosDevice,
    CarlosDeviceCreate,
    CarlosDeviceDriver,
    CarlosDeviceUpdate,
    create_device,
    get_device,
    get_device_drivers,
    list_devices,
    update_device,
    update_device_driver,
)
from carlos.database.device.device_metadata import (
    CarlosDeviceDriverUpdate,
    CarlosDeviceSignal,
    get_device_signals,
)
from carlos.edge.interface import DeviceId
from fastapi import APIRouter, Body, Depends, Path

from carlos.api.depends.context import request_context

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


@devices_router.get(
    "/{deviceId}/drivers",
    summary="Get all drivers for a device.",
    response_model=list[CarlosDeviceDriver],
)
async def get_device_drivers_route(
    device_id: DeviceId = DEVICE_ID_PATH,
    context: RequestContext = Depends(request_context),
):
    """Get all drivers for a device."""
    return await get_device_drivers(context=context, device_id=device_id)


DRIVER_IDENTIFIER_PATH: str = Path(
    ...,
    alias="driverIdentifier",
    description="The unique identifier of the driver.",
)


@devices_router.put(
    "/{deviceId}/drivers/{driverIdentifier}",
    summary="Update a driver for a device.",
    response_model=CarlosDeviceDriver,
)
async def update_device_driver_route(
    driver: CarlosDeviceDriverUpdate = Body(),
    device_id: DeviceId = DEVICE_ID_PATH,
    driver_identifier: str = DRIVER_IDENTIFIER_PATH,
    context: RequestContext = Depends(request_context),
):
    """Update a driver for a device."""
    return await update_device_driver(
        context=context,
        device_id=device_id,
        driver_identifier=driver_identifier,
        driver=driver,
    )


@devices_router.get(
    "/{deviceId}/drivers/{driverIdentifier}/signals",
    summary="Get all signals for a driver.",
    response_model=list[CarlosDeviceSignal],
)
async def get_device_signals_route(
    device_id: DeviceId = DEVICE_ID_PATH,
    driver_identifier: str = DRIVER_IDENTIFIER_PATH,
    context: RequestContext = Depends(request_context),
):
    """Get all signals for a driver."""
    return await get_device_signals(
        context=context, device_id=device_id, driver_identifier=driver_identifier
    )
