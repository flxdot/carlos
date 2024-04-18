from typing import Literal

from carlos.edge.interface.device import DigitalOutput, GpioConfig, IoFactory
from pydantic import Field

from carlos.edge.device.protocol import GPIO


class RelayConfig(GpioConfig):

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


IoFactory().register(ptype=__name__, config=RelayConfig, factory=Relay)
