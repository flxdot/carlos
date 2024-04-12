__all__ = ["public_router", "main_router"]

from fastapi import APIRouter, Security

from carlos.api.depends.authentication import cached_token_verify_from_env

from .device_server_routes import device_server_router
from .devices_routes import devices_router
from .health_routes import health_router

main_router = APIRouter(dependencies=[Security(cached_token_verify_from_env())])
"""This is the main router for the API. It is for routes that require authentication."""
main_router.include_router(devices_router, prefix="/devices", tags=["devices"])


public_router = APIRouter()
"""This route is for routes that are public and do not require authentication."""

public_router.include_router(health_router, prefix="/health", tags=["health"])
# The websocket endpoint needs to be secured individually.
public_router.include_router(device_server_router)
