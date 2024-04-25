from sqlalchemy import text

from carlos.edge.device.storage.connection import (
    build_storage_url,
    get_async_storage_engine,
    get_storage_engine,
)
from conftest import TEST_STORAGE_PATH


def test_get_storage_engine():
    engine = get_storage_engine(build_storage_url(TEST_STORAGE_PATH))

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1


async def test_get_async_storage_engine():
    engine = get_async_storage_engine(
        build_storage_url(TEST_STORAGE_PATH, is_async=True)
    )

    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        assert result.scalar() == 1
