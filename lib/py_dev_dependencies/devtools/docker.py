"""This module contains facade code for the docker api."""
import warnings

import time
from contextlib import suppress
from datetime import timedelta
from threading import Thread
from typing import Any, Callable

import docker  # type: ignore[import-untyped]
from docker.errors import DockerException  # type: ignore[import-untyped]
from docker.models.containers import Container  # type: ignore[import-untyped]
from docker.models.networks import Network  # type: ignore[import-untyped]
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings

__all__ = [
    "ContainerHandler",
    "ContainerManager",
    "DockerContainer",
    "PostgresContainer",
]


PortMapping = dict[str, int | tuple[str, int]]


class ContainerDefinition(BaseModel):
    """Used to provide a type safe interface for defining a container."""

    name: str = Field(..., description="The name of the container.")
    image: str = Field(..., description="The image to use for the container.")

    @field_validator("image")
    def validate_image(cls, value: str) -> str:
        """Ensures that the image is defined correctly."""
        if not value:
            raise ValueError("The image must not be empty.")
        if ":" not in value:
            raise ValueError("The image must have a tag.")

        image, tag = value.split(":")

        if not image:
            raise ValueError("The image must not be empty.")
        if not tag:
            raise ValueError("The tag must not be empty.")

        return value

    environment: dict[str, Any] = Field(
        default_factory=dict,
        description="A mapping of environment variables to apply to the container.",
    )
    ports: PortMapping = Field(
        default_factory=dict, description="A mapping of ports to expose."
    )

    @field_validator("ports")
    def validate_ports(cls, value: PortMapping) -> PortMapping:
        """Ensures the port mapping is given in the right format."""

        for container_port_def, host_port_def in value.items():
            container_port, container_protocol = container_port_def.split("/")
            if not container_port.isdigit():
                raise ValueError("The port must be an integer.")
            if container_protocol not in ("tcp", "upd", "sctp"):
                raise ValueError("The protocol must be one of 'tcp', 'upd', or 'sctp'.")

        return value

    volumes: list[str] = Field(
        default_factory=list,
        description="A list of volumes to mount into the container.",
    )


class DockerContainer:
    __CONTAINER_PURPOSE__ = "python-integration-testing"
    __NETWORK__ = "python-integration-testing-network"

    TIMEOUT = timedelta(seconds=15)

    def __init__(
        self,
        definition: ContainerDefinition,
    ):
        """Initializes the DockerContainer object.

        :param definition: The definition of the container.
        """

        self.name = definition.name
        self.image = definition.image
        self.environment = definition.environment
        self.ports = definition.ports
        self.volumes = definition.volumes

        self._container: Container | None = None
        self._network: Network | None = None

        try:
            self._client = docker.from_env()
        except DockerException as ex:  # pragma: no cover
            if "FileNotFoundError" in str(ex):
                raise DockerException(
                    "It seems as if the docker service is not running."
                ) from ex
            raise

    @property
    def container(self) -> Container:
        """Returns the container object."""
        if self._container is None:
            raise ValueError("Container has not been created yet.")  # pragma: no cover
        return self._container

    @property
    def network(self) -> Network:
        """Returns the network object."""
        if self._network is None:
            raise ValueError("Network has not been created yet.")  # pragma: no cover
        return self._network

    @staticmethod
    def convert_seconds_to_nano_seconds(seconds: int | float) -> int:
        return int(1e9 * seconds)

    def setup(self):
        """Creates the Database container."""

        rogue_containers = self._client.containers.list(
            all=True, filters={"name": self.name}
        )
        for container in rogue_containers:
            self.cleanup_container(container)  # pragma: no cover

        self._create_network()

        self.run()

    def _create_network(self):
        """Creates the required network in case it does not already exist."""

        network_name = self.__NETWORK__

        networks = self._client.networks.list()

        warnings.warn(f"Networks: {networks}")

        matching_networks = [
            network for network in networks if network.name == network_name
        ]

        if not matching_networks:  # pragma: no cover
            # if this line fails, you have probably too many docker networks.
            # clean them up with `docker network prune`
            try:
                self._network = self._client.networks.create(
                    name=network_name,
                    driver="bridge",
                    labels={"purpose": self.__NETWORK__},
                )
            except DockerException as ex:
                # When tests are failed or stopped during development, the
                # network might not be cleaned up properly. In this case, we
                # try to clean up the network and create a new one.
                if (
                    hasattr(ex, "explanation")
                    and "non-overlapping IPv4 address" in ex.explanation
                ):
                    for network in networks:
                        if network.name.startswith(self.__NETWORK__):
                            network.remove()
                    self._create_network()
                    return
                raise ex
            return

        self._network = matching_networks.pop(0)
        if matching_networks:  # pragma: no cover
            [network.remove() for network in matching_networks]

    def run(self):
        """Runs the container."""

        self._container = self._client.containers.run(
            **self.container_kwargs,
        )

    @property
    def container_kwargs(self) -> dict[str, Any]:
        """Builds the default container keyword arguments"""

        kwargs = {
            "detach": True,
            "environment": self.environment,
            "hostname": self.name,
            "image": self.image,
            "labels": {"name": self.name, "purpose": self.__CONTAINER_PURPOSE__},
            "name": self.name,
            "network": self.network.name,
        }

        if self.ports:
            kwargs["ports"] = self.ports
        if self.volumes:  # pragma: no cover
            kwargs["volumes"] = self.volumes

        return kwargs

    def is_healthy(self):
        """Checks if the container is healthy."""
        inspect_results = self._client.api.inspect_container(self.container.name)
        state = inspect_results["State"]
        if "Health" in state:
            health_status = state["Health"]["Status"]
            return health_status == "healthy"
        return False  # pragma: no cover

    def wait_for(
        self,
        timeout: float | None = None,
        health_check: Callable[[], bool] | None = None,
    ):
        """Wait for the container to get healthy"""

        actual_timeout: float = timeout or self.TIMEOUT.total_seconds()
        health_check_fcn: Callable[[], bool] = health_check or self.is_healthy

        start = time.time()
        while not health_check_fcn():
            if (time.time() - start) > actual_timeout:
                raise TimeoutError(  # pragma: no cover
                    f"Container did not get healthy within {actual_timeout} seconds."
                )
            time.sleep(0.1)

    def teardown(self):
        """Clean up the docker container"""

        self.cleanup_container()

    def cleanup_container(self, container: Container = None):
        """Cleans a given container"""

        if container is None:
            try:
                container = self.container
            except ValueError:
                # no need to clean up
                return

        if self.is_container_running(container):
            container.kill()
            container.wait(timeout=int(self.TIMEOUT.total_seconds()))

        with suppress(Exception):
            container.remove(v=True, force=True)

    def is_container_running(self, container: Container = None) -> bool:
        """Returns True if a container with the same name is already running."""
        if container is None:
            container_name = self.name
        else:
            container_name = container.name
        try:
            inspect_results = self._client.api.inspect_container(container_name)
        except docker.errors.NotFound:
            return False
        state = inspect_results["State"]

        return bool(state["Running"])


class PostgresContainer(DockerContainer):
    _IMAGE = "postgres"

    _HEALTH_CHECK_INTERVAL = timedelta(seconds=10)
    _HEALTH_CHECK_TIMEOUT = timedelta(seconds=5)
    _HEALTH_CHECK_RETRIES = 3

    def __init__(
        self,
        name: str,
        database_name: str,
        user: str,
        password: str,
        port: int,
        postgres_version: str = "16",
        environment: dict[str, Any] | None = None,
    ):

        definition = ContainerDefinition(
            name=name,
            image=f"{self._IMAGE}:{postgres_version}",
            environment=environment or {},
            ports={"5432/tcp": port},
        )

        super().__init__(
            definition=definition,
        )

        self.database_name = database_name
        self.user = user
        self.password = password
        self.port = port
        self.postgres_version = postgres_version

    def run(self):
        """Runs the container."""

        super().run()

        # wait for the container to become healthy
        self.wait_for()

    @property
    def container_kwargs(self) -> dict[str, Any]:
        """Builds the default container keyword arguments"""

        kwargs = super().container_kwargs

        kwargs["environment"].update(
            {
                "POSTGRES_DB": self.database_name,
                "POSTGRES_USER": self.user,
                "POSTGRES_PASSWORD": self.password,
                "PGDATA": "/var/lib/postgresql/data/pgdata",
            }
        )
        kwargs["healthcheck"] = {
            "Test": ["CMD-SHELL", "pg_isready"],
            "Interval": self.convert_seconds_to_nano_seconds(
                self._HEALTH_CHECK_INTERVAL.total_seconds()
            ),
            "timeout": self.convert_seconds_to_nano_seconds(
                self._HEALTH_CHECK_TIMEOUT.total_seconds()
            ),
            "retries": self._HEALTH_CHECK_RETRIES,
        }

        return kwargs


class ContainerHandler:
    """Handles the creation and teardown of the container."""

    def __init__(
        self,
        container: DockerContainer,
        post_setup: Callable[[], None] | None = None,
        setup_error_handler: Callable[[Exception], None] | None = None,
        teardown_fcn: Callable[[], None] | None = None,
    ):
        self.container = container
        self.post_setup = post_setup
        self.teardown_fcn = teardown_fcn
        self.setup_error_handler = (
            setup_error_handler or self._default_setup_error_handler
        )

        self.setup_error: Exception | None = None

    def _default_setup_error_handler(self, exception: Exception):
        """Prints the exception, stores it in the `setup_error` attribute a
        nd raises it again."""

        self.setup_error = exception

    def setup(self):
        """Initializes the context"""

        try:
            self.container.setup()
            if self.post_setup:
                self.post_setup()  # pragma: no cover
        except Exception as ex:
            self.setup_error_handler(ex)

    def teardown(self):
        """Ensures the context is torn down"""
        try:
            if self.teardown_fcn:
                self.teardown_fcn()  # pragma: no cover
        finally:
            self.container.teardown()


class ContainerManagerRunSettings(BaseSettings):
    RECYCLE_TEST_CONTAINER: bool = Field(
        False,
        description="Defines if the containers shall continue to run after the test"
        "and be reused for the next test.",
    )

    TEST_CONTAINER_PARALLEL_SETUP: bool = Field(
        True,
        description=(
            "If set to False, the containers will be created sequential "
            "instead of parallel. This can be useful for debugging errors happening "
            "during container setup or container post setup."
        ),
    )


class ContainerManager:
    """Parallelize the creation and teardown of the data sources via Threads."""

    def __init__(self, container_handlers: list[ContainerHandler] | None = None):
        self.container_handler: list[ContainerHandler] = []

        for handler in container_handlers or []:
            self.add(handler)

    def add(self, handler: ContainerHandler):
        if not isinstance(handler, ContainerHandler):
            raise TypeError(
                "Handler is not of type `ContainerHandler`."
            )  # pragma: no cover
        self.container_handler.append(handler)

    @property
    def container_names(self) -> tuple[str, ...]:
        return tuple(h.container.name for h in self.container_handler)

    def setup(self):
        """Create all registered data source handlers in parallel using threads."""

        container_run_settings = ContainerManagerRunSettings()

        all_container_exist = True
        for handler in self.container_handler:
            if not handler.container.is_container_running():
                all_container_exist = False
                break

        if container_run_settings.RECYCLE_TEST_CONTAINER and all_container_exist:
            return  # pragma: no cover

        if (
            container_run_settings.TEST_CONTAINER_PARALLEL_SETUP
            and len(self.container_handler) > 1
        ):
            threads = []
            for handler in self.container_handler:
                thread = Thread(
                    name="ContainerCreation" + handler.container.name,
                    target=handler.setup,
                )
                thread.start()
                threads.append(thread)

            [thread.join() for thread in threads]
            return

        [handler.setup() for handler in self.container_handler]

    def teardown(self):
        """Dispose all registered data source handlers in parallel using threads."""

        if not ContainerManagerRunSettings().RECYCLE_TEST_CONTAINER:
            [handler.teardown() for handler in self.container_handler]
