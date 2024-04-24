from functools import cache
from pathlib import Path

from sqlalchemy import Engine, NullPool, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from carlos.edge.device.constants import LOCAL_DEVICE_STORAGE_PATH

STORAGE_PATH = LOCAL_DEVICE_STORAGE_PATH / "storage.db"


def build_storage_url(path: Path = STORAGE_PATH, is_async: bool = False) -> str:
    """Build the storage URL for the device."""
    schema = "sqlite"
    if is_async:
        schema += "+aiosqlite"
    return f"{schema}:///{path.as_posix()}"


@cache
def get_storage_engine(url: str | None = None) -> Engine:
    """Get the storage engine for the device."""
    return create_engine(
        url or build_storage_url(), pool_pre_ping=True, poolclass=NullPool
    )


@cache
async def get_async_storage_engine(url: str | None = None) -> AsyncEngine:
    """Get the async storage engine for the device."""
    return create_async_engine(
        url or build_storage_url(is_async=True), pool_pre_ping=True, poolclass=NullPool
    )
