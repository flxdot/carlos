from functools import cache
from pathlib import Path

from carlos.edge.interface.data_directory import DATA_DIRECTORY
from sqlalchemy import Engine, NullPool, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

STORAGE_PATH = DATA_DIRECTORY / "device" / "storage.db"


def build_storage_url(path: Path = STORAGE_PATH, is_async: bool = False) -> str:
    """Build the storage URL for the device."""
    schema = "sqlite"
    if is_async:
        schema += "+aiosqlite"
    return f"{schema}:///{path.as_posix()}"


@cache
def get_storage_engine(url: str) -> Engine:
    """Get the storage engine for the device."""
    return create_engine(url, pool_pre_ping=True, poolclass=NullPool)


@cache
async def get_async_storage_engine(url: str) -> AsyncEngine:
    """Get the async storage engine for the device."""
    return create_async_engine(url, pool_pre_ping=True, poolclass=NullPool)