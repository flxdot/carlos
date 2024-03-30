"""This module contains the routes used by the carlos edge devices to receive data from
the API."""

__all__ = ["edge_router"]

from fastapi import APIRouter

edge_router = APIRouter()
