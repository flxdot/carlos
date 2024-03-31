"""This module contains a collection of context managers."""

__all__ = ["EnvironmentContext", "TemporaryWorkingDirectory"]

import os
from pathlib import Path
from typing import Any, Callable, Mapping


class EnvironmentContext:
    """A custom context manager that manages the environment."""

    def __init__(
        self,
        environment_variables: Mapping[str, Any],
        overwrite_existing: bool = False,
        echo: Callable[[str], None] | None = print,
    ):
        """Call the context manager with keyword arguments of the environment
        variables to be changed.

        :param environment_variables: A mapping with the names and values of the
            desired environment
        :param overwrite_existing: If set to True, already existing environment
            variables will be overwritten. Default: False
        :param echo: A function to echo the new environment. Default: print()
        """

        self._overwrite = overwrite_existing
        self._context_envs = environment_variables
        # little trick to print nothing
        self._echo = echo or (lambda x: None)
        self._cur_envs: dict[str, str | None] = {}

    def __enter__(self):
        """Sets the configured environment variables and saves current state."""

        self._echo("Setting environment variables:")

        self._cur_envs = {}
        for name, value in self._context_envs.items():
            self._cur_envs[name] = os.getenv(name)
            if not self._cur_envs[name] or self._overwrite:
                self._echo(f"{name}={value}")
                os.environ[name] = str(value)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Resets the environment variables back to it's original state."""

        for name, value in self._cur_envs.items():
            if value is None:
                os.environ.pop(name)
            else:
                os.environ[name] = value


class TemporaryWorkingDirectory:
    """Changes the working directory for the scope of the context manager to the
    specified path."""

    def __init__(self, directory: Path):
        assert directory.is_dir()

        self.temporary_working_dir = directory
        self.current_working_directory: Path | None = None

    def __enter__(self):
        self.current_working_directory = Path.cwd()
        os.chdir(self.temporary_working_dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.current_working_directory)
