from carlos.edge.interface.device import DigitalOutput, GpioConfig, IoFactory

from carlos.edge.device.protocol import GPIO


class Relay(DigitalOutput):
    """Relay."""

    def __init__(self, config: GpioConfig):
        super().__init__(config=config)

        GPIO.setup(self.config.pin, GPIO.OUT)

    def set(self, value: bool):
        """Writes the value to the relay."""
        GPIO.output(self.config.pin, value)


IoFactory().register(ptype=__name__, config=GpioConfig, factory=Relay)
