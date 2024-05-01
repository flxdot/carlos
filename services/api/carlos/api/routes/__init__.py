__all__ = ["public_router", "main_router"]

from fastapi import APIRouter, Security

from carlos.api.depends.authentication import verify_token

from .data_routes import data_router
from .device_server_routes import device_server_router
from .devices_routes import devices_router
from .health_routes import health_router
from .signals_routes import signals_router

main_router = APIRouter(dependencies=[Security(verify_token)])
"""This is the main router for the API. It is for routes that require authentication."""
main_router.include_router(data_router, prefix="/data", tags=["data"])
main_router.include_router(devices_router, prefix="/devices", tags=["devices"])
main_router.include_router(signals_router, prefix="/signals", tags=["signals"])

public_router = APIRouter()
"""This route is for routes that are public and do not require authentication."""

public_router.include_router(health_router, prefix="/health", tags=["health"])
# The websocket endpoint needs to be secured individually.
public_router.include_router(device_server_router)
