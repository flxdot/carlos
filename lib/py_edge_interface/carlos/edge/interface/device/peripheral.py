__all__ = ["AnalogInput", "DigitalOutput", "CarlosIO"]
import asyncio
import concurrent.futures
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from carlos.edge.interface.device.config import GPIOConfig, I2CConfig, IOConfig

Config = TypeVar("Config", I2CConfig, GPIOConfig, IOConfig)


class CarlosPeripheral(ABC, Generic[Config]):
    """Common base class for all peripherals."""

    def __init__(self, config: Config):
        self.config: Config = config


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
