"""This module contains the functions to perform the migrations of the
carlos database schema."""

__all__ = [
    "downgrade_carlos_schema",
    "migrate_carlos_schema",
    "setup_test_db_data",
]

import asyncio

from carlos.database.connection import get_async_carlos_database_engine
from carlos.database.testing.test_data import insert_carlos_database_test_data

from ._migrations import ALEMBIC_DIRECTORY
from .config import DatabaseConnectionSettings
from .utils import alembic_downgrade, alembic_upgrade, build_alembic_config


def migrate_carlos_schema(
    connection_settings: DatabaseConnectionSettings, revision: str | None = None
):
    """Migrates the database defined by the connection settings to the latest
    revision."""

    # bring the database to the most current schema version
    alembic_cfg = build_alembic_config(
        connection_settings=connection_settings, migration_directory=ALEMBIC_DIRECTORY
    )
    alembic_upgrade(alembic_cfg, revision=revision)


def downgrade_carlos_schema(
    connection_settings: DatabaseConnectionSettings, revision: str | None = None
):
    """Downgrades the database defined by the connection settings to the base revision.

    This function is hardly useful in production, but it is useful for testing."""

    # bring the database to the most current schema version
    alembic_cfg = build_alembic_config(
        connection_settings=connection_settings, migration_directory=ALEMBIC_DIRECTORY
    )
    alembic_downgrade(alembic_cfg, revision=revision)


def setup_test_db_data(
    connection_settings: DatabaseConnectionSettings,
):
    """Migrates the database defined by the connection settings to the latest
    revision and inserts the test data. Note that this function assumes that
    the database is on the latest revision of the carlos schema."""

    # migrate the carlos drivers schema
    migrate_carlos_schema(connection_settings=connection_settings)

    asyncio.run(setup_quality_test_db(connection_settings=connection_settings))


async def setup_quality_test_db(connection_settings: DatabaseConnectionSettings):
    """Inserts the test data required by the quality
    into the carlos database.

    This function assumes that the carlos schema as well as the
    quality schema are already migrated to the latest
    revision."""

    engine = get_async_carlos_database_engine(
        connection_settings=connection_settings, client_name="carlos.database pytest"
    )
    async with engine.connect() as connection:
        await insert_carlos_database_test_data(connection)

    await engine.dispose()


if __name__ == "__main__":  # pragma: no cover
    connection_settings = DatabaseConnectionSettings()

    migrate_carlos_schema(connection_settings=connection_settings)
