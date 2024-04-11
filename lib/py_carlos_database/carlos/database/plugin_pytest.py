from contextlib import asynccontextmanager
from functools import partial
from typing import AsyncIterator

import pytest
import pytest_asyncio
from devtools.converter import to_environment
from devtools.docker import ContainerHandler, ContainerManager, PostgresContainer
from devtools.networking import find_next_unused_port
from devtools.testing import setup_test_environment
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from carlos.database.config import DatabaseConnectionSettings
from carlos.database.connection import get_async_data_model_engine
from carlos.database.migration import setup_test_db_data

connection_settings = DatabaseConnectionSettings(
    host="localhost",
    port=find_next_unused_port(2347),
    name="postgres",
    user="postgres",
    password="postgres",
)


@pytest.fixture(scope="session", name="carlos_db_test_environment")
def fixture_test_environment():
    """Fixture to set up the temporary docker test database with test data"""

    container_handler = ContainerHandler(
        container=PostgresContainer(
            name="carlos-pytest-db",
            port=connection_settings.port,
            database_name=connection_settings.name,
            user=connection_settings.user,
            password=connection_settings.password.get_secret_value(),
        ),
        post_setup=partial(setup_test_db_data, connection_settings=connection_settings),
    )

    container_manager = ContainerManager(container_handlers=[container_handler])

    environment = to_environment(connection_settings)

    with setup_test_environment(
        container_manager=container_manager,
        environment=environment,
    ):
        yield


@asynccontextmanager
async def new_async_engine() -> AsyncIterator[AsyncEngine]:
    """Provides a global async engine to the test database"""

    async_engine = get_async_data_model_engine(
        connection_settings=connection_settings,
    )
    try:
        yield async_engine
    finally:
        await async_engine.dispose()


# The session scope works, due to the redefinition of the `event_loop` fixture
# above.
# see:
# https://pytest-asyncio.readthedocs.io/en/latest/reference/decorators.html
@pytest_asyncio.fixture(scope="session", name="async_carlos_db_engine")
async def fixture_async_engine() -> AsyncIterator[AsyncEngine]:
    """Provides a global async engine to the test database"""
    async with new_async_engine() as async_engine_:
        yield async_engine_


@pytest_asyncio.fixture(name="async_carlos_db_connection")
async def fixture_async_connection(
    async_carlos_db_engine: AsyncEngine,
) -> AsyncIterator[AsyncConnection]:
    """Provides a fresh async connection to the test database from the connection
    pool"""
    async with async_carlos_db_engine.connect() as conn:
        yield conn
