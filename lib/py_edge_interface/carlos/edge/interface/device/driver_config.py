__all__ = [
    "DRIVER_IDENTIFIER_LENGTH",
    "DirectionMixin",
    "DriverConfig",
    "DriverConfigWithDirection",
    "DriverDirection",
    "DriverMetadata",
    "DriverSignal",
    "GpioDriverConfig",
    "I2cDriverConfig",
]

import importlib
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, computed_field, field_validator

from carlos.edge.interface.types import CarlosSchema
from carlos.edge.interface.units import PhysicalQuantity, UnitOfMeasurement

# Pin layout
#   5V, 5V, GND,  14, 15, 18, GND, 23,   24, GND, 25,  8,   7, ID EEPROM, GND, 12, GND, 16, 20,  21 # Outer pins # noqa
# 3.3V,  2,  3,   4, GND, 17,  27, 22, 3.3V,  10,  9, 11, GND, ID EEPROM,   5,  6,  13, 19, 26, GND # Inner pins # noqa

DRIVER_IDENTIFIER_LENGTH = 64


class _DriverConfigMixin(CarlosSchema):
    """Common base class for all driver_module configurations."""

    identifier: str = Field(
        ...,
        max_length=DRIVER_IDENTIFIER_LENGTH,
        description="A unique identifier for the driver_module configuration. "
        "It is used to allow changing addresses, pins if required later.",
    )

    driver_module: str = Field(
        ...,
        description="Refers to the module name that implements the IO driver_module. "
        "Built-in drivers located in carlos.edge.device.driver module "
        "don't need to specify the full path. Each driver_module module"
        "must make a call to the DriverFactory.register method to register"
        "itself.",
    )


class DriverConfig(_DriverConfigMixin):
    """Common base class for all driver_module configurations."""

    @field_validator("driver_module", mode="after")
    def _validate_driver_module(cls, value):
        """Converts a module name to a full module path."""

        # check if the given module exists in the current working directory.
        try:
            importlib.import_module(value)
        except ModuleNotFoundError:
            abs_module = "carlos.edge.device.driver" + "." + value
            try:
                importlib.import_module(abs_module)
            except ModuleNotFoundError:
                raise ValueError(f"The module {value} ({abs_module}) does not exist.")
            value = abs_module  # pragma: no cover

        return value


class DriverDirection(StrEnum):
    """Enum for the direction of the IO."""

    INPUT = "input"
    OUTPUT = "output"
    BIDIRECTIONAL = "bidirectional"


class DirectionMixin(BaseModel):
    direction: DriverDirection = Field(..., description="The direction of the IO.")


class DriverConfigWithDirection(DriverConfig, DirectionMixin):
    pass


class GpioDriverConfig(DriverConfigWithDirection):
    """Defines a single input configuration."""

    protocol: Literal["gpio"] = Field(
        "gpio",
        description="The communication protocol to be used for the IO.",
    )

    pin: Literal[
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
    ] = Field(..., description="The GPIO pin number.")


class I2cDriverConfig(DriverConfigWithDirection):
    """Defines a single input configuration."""

    protocol: Literal["i2c"] = Field(
        "i2c",
        description="The communication protocol to be used for the IO.",
    )

    address: str = Field(..., description="The I2C address of the device.")

    @field_validator("address", mode="before")
    def validate_address(cls, value):
        """Validate the I2C address."""

        if isinstance(value, str):
            if value.startswith("0x"):
                value = value[2:]

            try:
                value = int(value, 16)
            except ValueError:
                raise ValueError("The I2C address must be a valid hexadecimal value.")

        # first 2 are reserved
        # address length is 7 bits, but the majority of literature defines 0x77 as max
        if not 0x03 <= int(value) <= 0x77:
            raise ValueError("The valid I2C address range is 0x03 to 0x77.")

        return f"0x{value:02x}"

    @property
    def address_int(self):
        """Returns the I2C address as an integer."""
        return int(self.address, 16)


class DriverSignal(CarlosSchema):
    """Defines the signals that the driver provides."""

    signal_identifier: str = Field(
        ...,
        description="A unique identifier of the signal within the context of a driver.",
    )

    unit_of_measurement: UnitOfMeasurement = Field(
        ...,
        description="The unit of measurement of the signal.",
    )

    @computed_field  # type: ignore
    @property
    def physical_quantity(self) -> PhysicalQuantity:  # pragma: no cover
        """Returns the physical quantity of this signal."""
        return self.unit_of_measurement.physical_quantity


class DriverMetadata(_DriverConfigMixin, DirectionMixin):
    """Provides the metadata for the driver."""

    signals: list[DriverSignal] = Field(
        ...,
        description="The signals that the driver provides.",
    )
