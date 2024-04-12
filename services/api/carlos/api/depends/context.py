from carlos.database.context import RequestContext
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncConnection

from .database import carlos_db_connection


async def request_context(
    connection: AsyncConnection = Depends(carlos_db_connection),
) -> RequestContext:
    """Creates a request context for the API."""
    return RequestContext(connection=connection)
