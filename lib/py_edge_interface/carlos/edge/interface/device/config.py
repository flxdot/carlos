__all__ = ["GpioConfig", "I2cConfig", "IoConfig"]

import importlib
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Pin layout
#   5V, 5V, GND,  14, 15, 18, GND, 23,   24, GND, 25,  8,   7, ID EEPROM, GND, 12, GND, 16, 20,  21 # Outer pins # noqa
# 3.3V,  2,  3,   4, GND, 17,  27, 22, 3.3V,  10,  9, 11, GND, ID EEPROM,   5,  6,  13, 19, 26, GND # Inner pins # noqa


class IoConfig(BaseModel):
    """Common base class for all IO configurations."""

    identifier: str = Field(
        ...,
        description="A unique identifier for the IO configuration. "
        "It is used to allow changing addresses, pins if required later.",
    )

    module: str = Field(
        ...,
        description="The module name that will be imported and registers itself in "
        "the IoFactory. If the module does not contain `.` it is assumed "
        "to be a built-in module.",
    )

    @field_validator("module", mode="after")
    def _validate_module(cls, value):
        """Converts a module name to a full module path."""

        # check if the given module exists in the current working directory.
        try:
            importlib.import_module(value)
        except ModuleNotFoundError:
            abs_module = "carlos.edge.device.io" + "." + value
            try:
                importlib.import_module(abs_module)
            except ModuleNotFoundError:  # pragma: no cover
                raise ValueError(f"The module {value} ({abs_module}) does not exist.")
            value = abs_module

        return value


class DirectionMixin(BaseModel):
    direction: Literal["input", "output"] = Field(
        ..., description="The direction of the IO."
    )


class GpioConfig(IoConfig, DirectionMixin):
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


class I2cConfig(IoConfig, DirectionMixin):
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

        return hex(value)

    @property
    def address_int(self):
        """Returns the I2C address as an integer."""
        return int(self.address, 16)
