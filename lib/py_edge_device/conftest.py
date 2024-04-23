from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import Connection, Engine

from carlos.edge.device.storage.connection import build_storage_url, get_storage_engine
from carlos.edge.device.storage.migration import (
    alembic_downgrade,
    alembic_upgrade,
    build_alembic_config,
)

TEST_STORAGE_PATH = Path(__file__).parent / "tests" / "storage.db"


@pytest.fixture()
def sync_engine() -> Generator[Engine, None, None]:
    """Fixture that provides a synchronous connection to a temporary SQLite database."""

    storage_url = build_storage_url(TEST_STORAGE_PATH)

    alembic_config = build_alembic_config(connection_url=storage_url)
    alembic_upgrade(alembic_config=alembic_config)

    yield get_storage_engine(url=storage_url)

    alembic_downgrade(alembic_config=alembic_config)


@pytest.fixture()
def sync_connection(sync_engine: Engine) -> Generator[Connection, None, None]:
    """Fixture that provides a synchronous connection to a temporary SQLite database."""

    with sync_engine.connect() as connection:
        yield connection
