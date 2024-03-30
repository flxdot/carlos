__all__ = ["public_router", "main_router"]

from fastapi import APIRouter

from .edge_routes import edge_router
from .health import health_router

main_router = APIRouter()
"""This is the main router for the API. It is for routes that require authentication."""
main_router.include_router(edge_router, prefix="/edge")

public_router = APIRouter()
"""This route is for routes that are public and do not require authentication."""
public_router.include_router(health_router, prefix="/health")
