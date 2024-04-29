__all__ = ["signals_router"]
from carlos.database.context import RequestContext
from carlos.database.device import (
    CarlosDeviceSignal,
    CarlosDeviceSignalUpdate,
    update_device_signal,
)
from fastapi import APIRouter, Body, Depends, Path

from carlos.api.depends.context import request_context

signals_router = APIRouter()


@signals_router.put(
    "/{timeseriesId}",
    summary="Update a signal by its ID.",
    response_model=CarlosDeviceSignal,
)
async def update_device_signal_route(
    signal: CarlosDeviceSignalUpdate = Body(),
    timeseries_id: int = Path(
        ...,
        alias="timeseriesId",
        description="The unique identifier of the signal.",
    ),
    context: RequestContext = Depends(request_context),
):
    """Update a signal by its ID."""
    return await update_device_signal(
        context=context, timeseries_id=timeseries_id, signal=signal
    )
