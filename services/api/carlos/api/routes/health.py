"""This module defines the route to determine the health of the API."""

__all__ = ["health_router"]

from fastapi import APIRouter

health_router = APIRouter()


@health_router.get("")
async def health():
    """Endpoint to determine the health of the API."""
    return {"status": "ok"}
