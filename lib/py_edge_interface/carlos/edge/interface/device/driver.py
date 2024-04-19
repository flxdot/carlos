__all__ = [
    "AnalogInput",
    "DigitalOutput",
    "CarlosDriver",
    "DriverFactory",
    "validate_device_address_space",
]
import asyncio
import concurrent.futures
from abc import ABC, abstractmethod
from collections import namedtuple
from time import sleep
from typing import Any, Callable, Generic, Iterable, Self, TypeVar

from .driver_config import (
    DirectionMixin,
    DriverConfig,
    GpioDriverConfig,
    I2cDriverConfig,
)

DriverConfigTypeVar = TypeVar("DriverConfigTypeVar", bound=DriverConfig)


class CarlosDriverBase(ABC, Generic[DriverConfigTypeVar]):
    """Common base class for all drivers."""

    def __init__(self, config: DriverConfigTypeVar):
        self.config: DriverConfigTypeVar = config

    def __str__(self):
        return f"{self.config.identifier} ({self.config.driver_module})"

    @property
    def identifier(self):
        return self.config.identifier

    @abstractmethod
    def setup(self) -> Self:
        """Sets up the peripheral. This is required for testing. As the test runner
        is not able to run the setup method of the peripheral outside the device."""
        pass

    @abstractmethod
    def test(self):
        """Tests the peripheral. This is used to validate a config by a human."""
        pass


class AnalogInput(CarlosDriverBase, ABC):
    """Common base class for all analog input peripherals."""

    def __init__(self, config: DriverConfigTypeVar):

        if isinstance(config, DirectionMixin):
            if config.direction != "input":
                raise ValueError(
                    "Recieved a non-input configuration for an analog input."
                )

        super().__init__(config)

    @abstractmethod
    def read(self) -> dict[str, float]:
        """Reads the value of the analog input. The return value is a dictionary
        containing the value of the analog input."""
        pass

    def test(self):
        """Tests the analog input by reading the value."""

        return self.read()

    async def read_async(self) -> dict[str, float]:
        """Reads the value of the analog input asynchronously. The return value is a
        dictionary containing the value of the analog input."""

        loop = asyncio.get_running_loop()

        with concurrent.futures.ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(executor=pool, func=self.read)


class DigitalOutput(CarlosDriverBase, ABC):
    """Common base class for all digital output peripherals."""

    def __init__(self, config: DriverConfigTypeVar):

        if isinstance(config, DirectionMixin):
            if config.direction != "output":
                raise ValueError(
                    "Recieved a non-output configuration for a digital output."
                )

        super().__init__(config)

    @abstractmethod
    def set(self, value: bool):
        pass

    def test(self):
        """Tests the digital output by setting the value to False, then True for 1 second,
        and then back to False."""

        self.set(False)
        self.set(True)
        sleep(1)
        self.set(False)


CarlosDriver = AnalogInput | DigitalOutput

DriverDefinition = namedtuple("DriverDefinition", ["config", "factory"])


class DriverFactory:
    """A singleton factory for io peripherals."""

    _instance = None
    _driver_index: dict[str, DriverDefinition] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DriverFactory, cls).__new__(cls)
            cls._instance._driver_index = {}

        return cls._instance

    def register(
        self,
        driver_module: str,
        config: type[DriverConfigTypeVar],
        factory: Callable[[DriverConfigTypeVar], CarlosDriver],
    ):
        """Registers a peripheral with the peripheral registry.

        :param driver_module: The peripheral type.
        :param config: The peripheral configuration model.
        :param factory: The peripheral factory function.
        :raises ValueError: If the config is not a subclass of DriverConfig.
        :raises RuntimeError: If the peripheral is already registered.
        """

        if not issubclass(config, DriverConfig):
            raise ValueError(
                "The config must be a subclass of DriverConfig. "
                "Please ensure that the config class is a subclass of DriverConfig."
            )

        if driver_module in self._driver_index:
            raise RuntimeError(f"The peripheral {driver_module} is already registered.")

        self._driver_index[driver_module] = DriverDefinition(config, factory)

    def build(self, config: dict[str, Any]) -> CarlosDriver:
        """Builds a IO object from its configuration.

        :param config: The raw configuration. The schema must adhere to the
            DriverConfig model. But we require the full config as the ios may require
            additional parameters.
        :returns: The IO object.
        :raises RuntimeError: If the driver is not registered.
        """

        io_config = DriverConfig.model_validate(config)

        if io_config.driver_module not in self._driver_index:
            raise RuntimeError(
                f"The driver {io_config.driver_module} is not registered."
                f"Make sure to register `DriverFactory().register(...)` "
                f"the peripheral before building it."
            )

        driver_definition = self._driver_index[io_config.driver_module]

        return driver_definition.factory(
            driver_definition.config.model_validate(config)
        )


I2C_PINS = [2, 3]
"""The Pin numbers designated for I2C communication."""


def validate_device_address_space(drivers: Iterable[CarlosDriver]):
    """This function ensures that the configured pins and addresses are unique.

    :param drivers: The list of IOs to validate.
    :raises ValueError: If any of the pins or addresses are configured more than once.
        If the GPIO pins 2 and 3 are when I2C communication is configured.
        If any of the identifiers are configured more than once.
    """

    # Ensure all identifiers are unique
    seen_identifiers = set()
    duplicate_identifiers = [
        driver.identifier
        for driver in drivers
        if driver.identifier in seen_identifiers or seen_identifiers.add(driver.identifier)  # type: ignore[func-returns-value] # noqa: E501
    ]
    if duplicate_identifiers:
        raise ValueError(
            f"The identifiers {duplicate_identifiers} are configured more than "
            f"once. Please ensure that each identifier is configured only once."
        )

    configs = [io.config for io in drivers]

    gpio_configs: list[GpioDriverConfig] = [
        io for io in configs if isinstance(io, GpioDriverConfig)
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

    i2c_configs: list[I2cDriverConfig] = [
        io for io in configs if isinstance(io, I2cDriverConfig)
    ]
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
