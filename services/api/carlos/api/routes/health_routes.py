"""This module defines the route to determine the health of the API."""

__all__ = ["health_router"]

from enum import Enum

from carlos.database.schema import CarlosSchema
from fastapi import APIRouter, Depends
from pydantic import Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.responses import JSONResponse
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE

from carlos.api.depends.database import carlos_db_connection

health_router = APIRouter()


class HealthStatus(str, Enum):
    """The status of the API."""

    OK = "ok"
    NO_DB_CONNECTION = "no_db_connection"
    ERROR = "error"


class HealthResponse(CarlosSchema):
    """Defines the status of the API."""

    status: HealthStatus = Field(..., description="The status of the API.")
    message: str = Field(..., description="A message about the status of the API.")


@health_router.get("", response_model=HealthResponse, tags=["health"])
async def health(connection: AsyncConnection = Depends(carlos_db_connection)):
    """Endpoint to determine the health of the API."""

    try:
        await connection.execute(text("SELECT 1"))
    except Exception:  # pragma: no cover
        return JSONResponse(
            content=HealthResponse(
                status=HealthStatus.NO_DB_CONNECTION,
                message="Could not establish a connection to the database.",
            ),
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
        )

    return HealthResponse(status=HealthStatus.OK, message="The API is functional.")
