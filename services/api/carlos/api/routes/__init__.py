__all__ = ["public_router", "main_router"]

from fastapi import APIRouter, Security

from carlos.api.depends.authentication import VerifyToken

from .device_server_routes import device_server_router
from .health_routes import health_router

# todo: activate authentication
authentication = VerifyToken()
main_router = APIRouter(dependencies=[Security(authentication.verify)])
# main_router = APIRouter()
"""This is the main router for the API. It is for routes that require authentication."""


public_router = APIRouter()
"""This route is for routes that are public and do not require authentication."""

public_router.include_router(health_router, prefix="/health")
# The websocket endpoint needs to be secured individually.
public_router.include_router(device_server_router)
