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

        # HIGH means off, LOW means
        GPIO.setup(self.config.pin, GPIO.OUT, initial=GPIO.HIGH)

    def set(self, value: bool):
        """Writes the value to the relay."""

        # HIGH means off, LOW means on
        GPIO.output(self.config.pin, GPIO.LOW if value else GPIO.HIGH)


DriverFactory().register(driver_module=__name__, config=RelayConfig, factory=Relay)
