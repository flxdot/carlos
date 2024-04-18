__all__ = [
    "AnalogInput",
    "DigitalOutput",
    "CarlosIO",
    "IoFactory",
    "validate_device_address_space",
]
import asyncio
import concurrent.futures
from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Any, Callable, Generic, Iterable, TypeVar

from .config import GpioConfig, I2cConfig, IoConfig

IoConfigTypeVar = TypeVar("IoConfigTypeVar", bound=IoConfig)


class CarlosPeripheral(ABC, Generic[IoConfigTypeVar]):
    """Common base class for all peripherals."""

    def __init__(self, config: IoConfigTypeVar):
        self.config: IoConfigTypeVar = config

    def __str__(self):
        return f"{self.config.identifier} ({self.config.module})"

    @abstractmethod
    def setup(self):
        """Sets up the peripheral. This is required for testing. As the test runner
        is not able to run the setup method of the peripheral outside the device."""
        pass


class AnalogInput(CarlosPeripheral, ABC):
    """Common base class for all analog input peripherals."""

    @abstractmethod
    def read(self) -> dict[str, float]:
        """Reads the value of the analog input. The return value is a dictionary
        containing the value of the analog input."""
        pass

    async def read_async(self) -> dict[str, float]:
        """Reads the value of the analog input asynchronously. The return value is a dictionary
        containing the value of the analog input."""

        loop = asyncio.get_running_loop()

        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(executor=pool, func=self.read)


class DigitalOutput(CarlosPeripheral, ABC):
    """Common base class for all digital output peripherals."""

    @abstractmethod
    def set(self, value: bool):
        pass


CarlosIO = AnalogInput | DigitalOutput

FactoryItem = namedtuple("FactoryItem", ["config", "factory"])


class IoFactory:
    """A singleton factory for io peripherals."""

    _instance = None
    _driver_to_io_type: dict[str, FactoryItem] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IoFactory, cls).__new__(cls)
            cls._instance._driver_to_io_type = {}

        return cls._instance

    def register(
        self,
        ptype: str,
        config: type[IoConfigTypeVar],
        factory: Callable[[IoConfigTypeVar], CarlosIO],
    ):
        """Registers a peripheral with the peripheral registry.

        :param ptype: The peripheral type.
        :param config: The peripheral configuration model.
        :param factory: The peripheral factory function.
        """

        if not issubclass(config, IoConfig):
            raise ValueError(
                "The config must be a subclass of IoConfig. "
                "Please ensure that the config class is a subclass of IoConfig."
            )

        if ptype in self._driver_to_io_type:
            raise RuntimeError(f"The peripheral {ptype} is already registered.")

        self._driver_to_io_type[ptype] = FactoryItem(config, factory)

    def build(self, config: dict[str, Any]) -> CarlosIO:
        """Builds a IO object from its configuration.

        :param config: The raw configuration. The schema must adhere to the
            IoConfig model. But we require the full config as the ios may require
            additional parameters.
        :returns: The IO object.
        """

        io_config = IoConfig.model_validate(config)

        if io_config.driver not in self._driver_to_io_type:
            raise RuntimeError(
                f"The driver {io_config.driver} is not registered."
                f"Make sure to register `IoFactory().register(...)` "
                f"the peripheral before building it."
            )

        entry = self._driver_to_io_type[io_config.driver]

        return entry.factory(entry.config.model_validate(config))


I2C_PINS = [2, 3]
"""The Pin numbers designated for I2C communication."""


def validate_device_address_space(ios: Iterable[CarlosIO]):
    """This function ensures that the configured pins and addresses are unique.

    :param ios: The list of IOs to validate.
    :raises ValueError: If any of the pins or addresses are configured more than once.
        If the GPIO pins 2 and 3 are when I2C communication is configured.
        If any of the identifiers are configured more than once.
    """

    configs = [io.config for io in ios]

    gpio_configs: list[GpioConfig] = [
        io for io in configs if isinstance(io, GpioConfig)
    ]

    # Ensure GPIO pins are unique
    seen_pins = set()
    duplicate_gpio_pins = [
        gpio.pin
        for gpio in gpio_configs
        if gpio.pin in seen_pins or seen_pins.add(gpio.pin)  # type: ignore[func-returns-value] # noqa: E501
    ]
    if duplicate_gpio_pins:
        raise ValueError(
            f"The GPIO pins {duplicate_gpio_pins} are configured more than once."
            f"Please ensure that each GPIO pin is configured only once."
        )

    i2c_configs: list[I2cConfig] = [io for io in configs if isinstance(io, I2cConfig)]
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
        if i2c.address in i2c_configs or seen_addresses.add(i2c.address)  # type: ignore[func-returns-value] # noqa: E501
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
        for io in configs
        if io.identifier in seen_identifiers or seen_identifiers.add(io.identifier)  # type: ignore[func-returns-value] # noqa: E501
    ]
    if duplicate_identifiers:
        raise ValueError(
            f"The identifiers {duplicate_identifiers} are configured more than "
            f"once. Please ensure that each identifier is configured only once."
        )
