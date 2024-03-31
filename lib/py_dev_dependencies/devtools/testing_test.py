import os
import secrets

import docker
import pytest

from devtools.docker import (
    ContainerDefinition,
    ContainerHandler,
    ContainerManager,
    DockerContainer,
    PostgresContainer,
)

from .networking import find_next_unused_port
from .testing import setup_test_environment


@pytest.mark.parametrize(
    "container_manager, environment",
    [
        pytest.param(ContainerManager(), None, id="nothing"),
        pytest.param(
            ContainerManager(
                container_handlers=[
                    ContainerHandler(
                        container=DockerContainer(
                            ContainerDefinition(name="nginx-1", image="nginx:latest")
                        )
                    ),
                    ContainerHandler(
                        container=PostgresContainer(
                            name="pg-database",
                            database_name="my_custom_db",
                            user="new_default_user",
                            password=secrets.token_urlsafe(8),
                            port=find_next_unused_port(5432),
                        )
                    ),
                ]
            ),
            {"TEST_ENV": "test_value", "TEST_ENV2": "test_value2"},
            id="everything",
        ),
    ],
)
def test_setup_test_environment(
    container_manager: ContainerManager, environment: dict[str, str] | None
):
    """This test ensures that the `setup_test_environment` function works as
    expected."""

    docker_client = docker.from_env()

    with setup_test_environment(
        container_manager=container_manager, environment=environment
    ):

        # ensure that all environment variables are set
        for key, value in (environment or {}).items():
            assert os.getenv(key) == value

        running_containers = docker_client.containers.list()
        for expected_container_name in container_manager.container_names:
            assert any(
                c.name == expected_container_name for c in running_containers
            ), f"Container {expected_container_name} not found"


def test_setupt_test_environment_errors():
    """This test ensures that the approriate error functinos are called in case the
    container setup fails."""

    setup_failed = False

    def on_setup_error(message: str):
        nonlocal setup_failed
        setup_failed = True

    container_handler = ContainerHandler(
        container=DockerContainer(
            ContainerDefinition(
                name="image-does-not-exist",
                image=f"{secrets.token_hex(16)}:{secrets.token_hex(4)}",
            )
        )
    )

    with setup_test_environment(
        container_manager=ContainerManager([container_handler]),
        pytest_failure_fcn=on_setup_error,
    ):
        pass

    assert setup_failed, "The failure function was not called."
