__all__ = ["carlos_db_connection"]

from typing import AsyncGenerator

from carlos.database.connection import get_async_carlos_db_connection
from sqlalchemy.ext.asyncio import AsyncConnection


async def carlos_db_connection() -> AsyncGenerator[AsyncConnection, None]:
    """Draws a connection from the connection pool to the Carlos database."""
    async with get_async_carlos_db_connection(client_name="Carlos API") as con:
        yield con
