"""This module defines the route to determine the health of the API."""

__all__ = ["health_router"]

from enum import Enum

from carlos.database.schema import CarlosSchema
from fastapi import APIRouter
from pydantic import Field
from sqlalchemy import text
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
async def health():
    """Endpoint to determine the health of the API."""

    try:
        async for con in carlos_db_connection():
            await con.execute(text("SELECT 1"))
            break
    except Exception:  # pragma: no cover
        return JSONResponse(
            content=HealthResponse(
                status=HealthStatus.NO_DB_CONNECTION,
                message="Could not establish a connection to the database.",
            ).model_dump(mode="json"),
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
        )

    return HealthResponse(status=HealthStatus.OK, message="The API is functional.")
