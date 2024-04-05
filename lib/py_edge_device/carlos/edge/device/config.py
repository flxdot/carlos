"""The config module contains code to define, validate, read, write and update the
configuration of the application."""

__all__ = [
    "DeviceConfig",
    "read_config",
    "read_config_file",
    "write_config",
    "write_config_file",
]

from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel, Field

from carlos.edge.device.constants import CONFIG_FILE_NAME


class DeviceConfig(BaseModel):
    """Configures the pure device settings."""

    device_id: str = Field(..., description="The unique identifier of the device.")


Config = TypeVar("Config", bound=BaseModel)


def read_config_file(path: Path, schema: type[Config]) -> Config:
    """Reads the configuration from the current working directory."""

    with open(path, "r") as file:
        return schema.model_validate(yaml.safe_load(file))


def write_config_file(path: Path, config: Config):
    """Writes the configuration to the current working directory."""

    if not path.parent.exists():
        path.parent.mkdir(parents=True)  # pragma: no cover

    with open(path, "w") as file:
        yaml.safe_dump(
            # do not export default values or unset values in order to allow
            # to change the default behavior in the future
            data=config.model_dump(mode="json", exclude_unset=True),
            stream=file,
        )


def read_config() -> DeviceConfig:  # pragma: no cover
    """Reads the configuration from the default location."""

    return read_config_file(
        path=Path.cwd() / CONFIG_FILE_NAME,
        schema=DeviceConfig,
    )


def write_config(config: DeviceConfig):  # pragma: no cover
    """Writes the configuration to the default location."""
    write_config_file(path=Path.cwd() / CONFIG_FILE_NAME, config=config)
