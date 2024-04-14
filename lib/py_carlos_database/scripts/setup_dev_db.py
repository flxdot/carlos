"""This script can be used to insert the test data into a local test database."""

from functools import partial
from time import sleep

from devtools.converter import to_environment
from devtools.docker import ContainerHandler, ContainerManager, PostgresContainer
from devtools.testing import setup_test_environment

from carlos.database.config import DatabaseConnectionSettings
from carlos.database.migration import setup_test_db_data

if __name__ == "__main__":

    connection_settings = DatabaseConnectionSettings()

    container_handler = ContainerHandler(
        container=PostgresContainer(
            name="carlos-dev-db",
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
        while True:
            sleep(1)
