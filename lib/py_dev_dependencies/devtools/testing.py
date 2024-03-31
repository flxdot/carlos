__all__ = ["setup_test_environment"]

from contextlib import contextmanager
from typing import Callable, Iterator

import pytest
from loguru import logger

from devtools.context_manager import EnvironmentContext
from devtools.docker import ContainerManager


@contextmanager
def setup_test_environment(
    container_manager: ContainerManager,
    environment: dict[str, str] | None = None,
    pytest_failure_fcn: Callable[[str], None] = pytest.exit,
) -> Iterator[None]:
    """Little helper to setup a test environment.

    :param container_manager: The container manager to setup and teardown.
    :param environment: A dictionary with environment variables to set.
    :param pytest_failure_fcn: The function to call in case of a failure. This is used
    to allow testing of this function. But usually, you should not need to change this.
    """

    with EnvironmentContext(environment or {}):
        container_names = ", ".join(container_manager.container_names)

        try:
            logger.info(f"Setting up testing containers: {container_names}")
            container_manager.setup()

            # check for any error during container setup
            for handler in container_manager.container_handler:
                if handler.setup_error is not None:
                    # There seems to be issue with the coverage here. The code is
                    # actually tested in the test file.
                    pytest_failure_fcn(  # pragma: no cover
                        f"Failed to initialize container: {handler.container.name}:"
                        f"\n\n{handler.setup_error}"
                    )

            logger.info(f"Finished setting up testing containers: {container_names}")
            yield None
        except Exception as e:  # pragma: no cover
            logger.error(e)
            pytest_failure_fcn(f"Container setup failed, skipping test suit: {e}")
            yield None  # used for testing only. Usually this code is not reachable.
        finally:
            container_manager.teardown()
