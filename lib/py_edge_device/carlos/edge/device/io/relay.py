from carlos.edge.interface.device import DigitalOutput, GPIOConfig, peripheral_registry

from carlos.edge.device.protocol import GPIO


class Relay(DigitalOutput):
    """Relay."""

    def __init__(self, config: GPIOConfig):
        super().__init__(config=config)

        GPIO.setup(self.config.pin, GPIO.OUT)

    def write(self, value: bool):
        """Writes the value to the relay."""
        GPIO.output(self.config.pin, value)


peripheral_registry.register(ptype=__name__, config=GPIOConfig, factory=Relay)
