from typing import Literal

from carlos.edge.interface.device import DigitalOutput, DriverFactory, GpioDriverConfig
from pydantic import Field

from carlos.edge.device.protocol import GPIO


class RelayConfig(GpioDriverConfig):

    direction: Literal["output"] = Field("output")


class Relay(DigitalOutput):
    """Relay."""

    def __init__(self, config: RelayConfig):
        super().__init__(config=config)

    def setup(self):
        GPIO.setup(self.config.pin, GPIO.OUT, initial=GPIO.LOW)

    def set(self, value: bool):
        """Writes the value to the relay."""
        GPIO.output(self.config.pin, value)


DriverFactory().register(ptype=__name__, config=RelayConfig, factory=Relay)
