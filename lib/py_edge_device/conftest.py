from pathlib import Path
from typing import Generator

import pytest
import pytest_asyncio
from sqlalchemy import Connection, Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from carlos.edge.device.storage.connection import (
    build_storage_url,
    get_async_storage_engine,
    get_storage_engine,
)
from carlos.edge.device.storage.migration import (
    alembic_downgrade,
    alembic_upgrade,
    build_alembic_config,
)

TEST_STORAGE_PATH = Path(__file__).parent / "tests" / "storage.db"


@pytest.fixture(autouse=True, scope="session")
def db_migration() -> None:
    """Fixture that upgrades the database and downgrades it after the test."""

    alembic_config = build_alembic_config(
        connection_url=build_storage_url(TEST_STORAGE_PATH)
    )
    alembic_upgrade(alembic_config=alembic_config)

    yield

    alembic_downgrade(alembic_config=alembic_config)


@pytest.fixture()
def sync_engine() -> Generator[Engine, None, None]:
    """Fixture that provides a synchronous connection to a temporary SQLite database."""

    yield get_storage_engine(url=build_storage_url(TEST_STORAGE_PATH))


@pytest.fixture()
def sync_connection(sync_engine: Engine) -> Generator[Connection, None, None]:
    """Fixture that provides a synchronous connection to a temporary SQLite database."""

    with sync_engine.connect() as connection:
        yield connection


@pytest_asyncio.fixture()
async def async_engine() -> Generator[AsyncEngine, None, None]:
    """Fixture that provides an asynchronous connection to a temporary
    SQLite database."""

    yield get_async_storage_engine(
        url=build_storage_url(TEST_STORAGE_PATH, is_async=True)
    )


@pytest_asyncio.fixture()
async def async_connection(
    async_engine: AsyncEngine,
) -> Generator[Connection, None, None]:
    """Fixture that provides an asynchronous connection to a temporary
    SQLite database."""

    async with async_engine.connect() as connection:
        yield connection
