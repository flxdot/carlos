__all__ = [
    "AnalogInput",
    "CarlosIO",
    "DeviceConfig",
    "DigitalOutput",
    "GPIOConfig",
    "I2CConfig",
    "IOConfig",
    "PeripheralConfig",
    "peripheral_registry",
]

from .config import DeviceConfig, GPIOConfig, I2CConfig, IOConfig, PeripheralConfig
from .io import peripheral_registry
from .peripheral import AnalogInput, CarlosIO, DigitalOutput
