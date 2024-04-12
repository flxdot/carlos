import asyncio
from typing import Iterator

import pytest
from _pytest.fixtures import FixtureRequest

from carlos.database.migration import downgrade_carlos_schema, setup_test_db_data
from carlos.database.plugin_pytest import connection_settings


def ensure_migration_is_reversible():
    """This function is called by the environment setup fixture to ensure that
    the migration is reversible. This is done by migrating the database to the
    base and setting it up again 2 times. If the migration is not reversible,
    this will fail."""

    for _ in range(2):
        downgrade_carlos_schema(connection_settings=connection_settings)
        setup_test_db_data(connection_settings=connection_settings)

    # and one final tear down
    downgrade_carlos_schema(connection_settings=connection_settings)


@pytest.fixture(scope="session", autouse=True)
def test_environment(carlos_db_test_environment):
    """Fixture to set up the temporary docker test database with test data"""

    yield

    ensure_migration_is_reversible()
