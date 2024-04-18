__all__ = ["GpioConfig", "I2cConfig", "IoConfig", "IoPtypeDict"]

from abc import ABC
from typing import Literal, TypedDict

from pydantic import BaseModel, Field, field_validator

# Pin layout
#   5V, 5V, GND,  14, 15, 18, GND, 23,   24, GND, 25,  8,   7, ID EEPROM, GND, 12, GND, 16, 20,  21 # Outer pins # noqa
# 3.3V,  2,  3,   4, GND, 17,  27, 22, 3.3V,  10,  9, 11, GND, ID EEPROM,   5,  6,  13, 19, 26, GND # Inner pins # noqa


class IoPtypeDict(TypedDict):
    ptype: str


class IoConfig(BaseModel, ABC):
    """Common base class for all IO configurations."""

    identifier: str = Field(
        ...,
        description="A unique identifier for the IO configuration. "
        "It is used to allow changing addresses, pins if required later.",
    )

    ptype: str = Field(
        ...,
        description="A string that uniquely identifies the type of IO. Usually the "
        "name of the sensor or actuator in lower case letters.",
    )

    direction: Literal["input", "output"] = Field(
        ..., description="The direction of the IO."
    )


class GpioConfig(IoConfig):
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


class DigitalGpioOutputConfig(GpioConfig):
    """Defines a single digital output configuration."""

    direction: Literal["output"] = Field(
        ..., description="The direction of the GPIO pin."
    )


class I2cConfig(IoConfig):
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
