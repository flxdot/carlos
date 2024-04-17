__all__ = ["DeviceConfig"]

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

# Pin layout
#   5V, 5V, GND,  14, 15, 18, GND, 23,   24, GND, 25,  8,   7, ID EEPROM, GND, 12, GND, 16, 20,  21 # Outer pins # noqa
# 3.3V,  2,  3,   4, GND, 17,  27, 22, 3.3V,  10,  9, 11, GND, ID EEPROM,   5,  6,  13, 19, 26, GND # Inner pins # noqa

ProtocolConfig = Literal["i2c", "gpio"]


class IOConfig(BaseModel):
    """Common base class for all IO configurations."""

    identifier: str = Field(
        ...,
        description="A unique identifier for the IO configuration. "
        "It is used to allow changing addresses, pins if required later.",
    )

    protocol: ProtocolConfig = Field(
        ...,
        description="The communication protocol to be used for the IO.",
    )

    type: str = Field(
        ...,
        description="A string that uniquely identifies the type of IO. Usually the "
        "name of the sensor or actuator in lower case letters.",
    )

    direction: Literal["input", "output"] = Field(
        ..., description="The direction of the IO."
    )


class GPIOConfig(IOConfig):
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


class DigitalGPIOOutputConfig(GPIOConfig):
    """Defines a single digital output configuration."""

    direction: Literal["output"] = Field(
        ..., description="The direction of the GPIO pin."
    )


I2C_PINS = [2, 3]
"""The Pin numbers designated for I2C communication."""


class I2CConfig(BaseModel):
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


class DeviceConfig(BaseModel):
    """Configures the pure device settings."""

    io: list[GPIOConfig | I2CConfig] = Field(
        default_factory=list, description="A list of IO configurations."
    )

    @model_validator(mode="after")
    def _validate_address_or_pin_overlap(self):
        """This function ensures that the configured pins and addresses are unique."""
        gpio_configs = [io for io in self.io if isinstance(io, GPIOConfig)]

        # Ensure GPIO pins are unique
        seen_pins = set()
        duplicate_gpio_pins = [
            gpio.pin
            for gpio in gpio_configs
            if gpio.pin in seen_pins or seen_pins.add(gpio.pin)
        ]
        if duplicate_gpio_pins:
            raise ValueError(
                f"The GPIO pins {duplicate_gpio_pins} are configured more than once."
                f"Please ensure that each GPIO pin is configured only once."
            )

        i2c_configs = [io for io in self.io if isinstance(io, I2CConfig)]
        if i2c_configs:
            if any(gpio.pin in I2C_PINS for gpio in gpio_configs):
                raise ValueError(
                    "The GPIO pins 2 and 3 are reserved for I2C communication."
                    "Please use other pins for GPIO configuration."
                )

        # Ensure I2C addresses are unique
        seen_addresses = set()
        duplicate_i2c_addresses = [
            i2c.address
            for i2c in i2c_configs
            if i2c.address in i2c_configs or seen_addresses.add(i2c.address)
        ]
        if duplicate_i2c_addresses:
            raise ValueError(
                f"The I2C addresses {duplicate_i2c_addresses} are configured more than "
                f"once. Please ensure that each I2C address is configured only once."
            )

        # Ensure all identifiers are unique
        seen_identifiers = set()
        duplicate_identifiers = [
            io.identifier
            for io in self.io
            if io.identifier in seen_identifiers or seen_identifiers.add(io.identifier)
        ]
        if duplicate_identifiers:
            raise ValueError(
                f"The identifiers {duplicate_identifiers} are configured more than "
                f"once. Please ensure that each identifier is configured only once."
            )
