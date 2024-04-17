__all__ = ["DeviceConfig"]
from typing import Literal

from pydantic import BaseModel, Field

# Pin layout
#   5V, 5V, GND,  14, 15, 18, GND, 23,   24, GND, 25,  8,   7, ID EEPROM, GND, 12, GND, 16, 20,  21 # Outer pins # noqa
# 3.3V,  2,  3,   4, GND, 17,  27, 22, 3.3V,  10,  9, 11, GND, ID EEPROM,   5,  6,  13, 19, 26, GND # Inner pins # noqa

PINS = list(range(2, 28))
"""The Pin numbers available for GPIO communication."""


class GPIOInputConfig(BaseModel):
    """Defines a single input configuration."""

    display_name: str = Field(..., description="User defined name to be displayed in the UI.")



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


I2C_PINS = [2, 3]
"""The Pin numbers designated for I2C communication."""


class I2CInputConfig(BaseModel):
    """Defines a single input configuration."""


class DeviceConfig(BaseModel):
    """Configures the pure device settings."""

    inputs: list[InputConfig] = Field(
        default_factory=list, description="The input configuration."
    )
