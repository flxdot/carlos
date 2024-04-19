"""The config module contains code to define, validate, read, write and update the
configuration of the application."""

__all__ = [
    "load_drivers",
    "read_config_file",
    "write_config_file",
]

from pathlib import Path
from typing import TypeVar

import yaml
from carlos.edge.interface.device import CarlosDriver, DriverConfig, DriverFactory
from loguru import logger
from pydantic import BaseModel

from carlos.edge.device.constants import CONFIG_FILE_NAME
from carlos.edge.device.driver.device_metrics import DeviceMetrics

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


def load_drivers(config_dir: Path | None = None) -> list[CarlosDriver]:
    """Reads the configuration from the default location."""
    config_dir = config_dir or Path.cwd()

    with open(config_dir / CONFIG_FILE_NAME, "r") as file:
        raw_config = yaml.safe_load(file)

    factory = DriverFactory()

    try:
        driver_configs = [factory.build(config) for config in raw_config["drivers"]]
    except KeyError:  # pragma: no cover
        raise KeyError(
            f"The configuration file {config_dir / CONFIG_FILE_NAME} must contain "
            f"a 'drivers' key."
        )

    # We always want to have some device metrics
    if not any(isinstance(driver, DeviceMetrics) for driver in driver_configs):
        driver_configs.insert(
            0,
            factory.build(
                DriverConfig(
                    identifier="__device_metrics__",
                    driver_module=DeviceMetrics.__module__,
                ).model_dump()
            ),
        )

    logger.info(
        f"Loaded {len(driver_configs)} IOs: "
        f"{', '.join(str(io) for io in driver_configs)}"
    )

    return driver_configs
