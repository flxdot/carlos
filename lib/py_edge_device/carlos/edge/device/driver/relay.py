import time

from carlos.edge.interface.device import (
    DigitalInput,
    DigitalOutput,
    DriverDirection,
    DriverFactory,
    GpioDriverConfig,
)
from pydantic import Field

from carlos.edge.device.protocol import GPIO


class RelayConfig(GpioDriverConfig):

    direction: DriverDirection = Field(DriverDirection.BIDIRECTIONAL)


class Relay(DigitalOutput, DigitalInput):
    """Relay."""

    def __init__(self, config: RelayConfig):
        super().__init__(config=config)

    def setup(self):

        # HIGH means off, LOW means
        GPIO.setup(self.config.pin, GPIO.OUT, initial=GPIO.HIGH)

    def set(self, value: bool):
        """Writes the value to the relay."""

        GPIO.setup(self.config.pin, GPIO.OUT)
        # HIGH means off, LOW means on
        GPIO.output(self.config.pin, GPIO.LOW if value else GPIO.HIGH)

    def read(self) -> dict[str, bool]:
        """Reads the value of the relay."""

        GPIO.setup(self.config.pin, GPIO.IN)
        return {"value": bool(GPIO.input(self.config.pin))}

    def test(self):
        """Tests the relay by reading the value."""

        self.set(False)
        time.sleep(0.01)
        if self.read() is not False:
            raise ValueError("Value of relay was not set to false.")

        self.set(True)
        time.sleep(1)
        if self.read() is not True:
            raise ValueError("Value of relay was not set to true.")

        self.set(False)
        time.sleep(0.01)
        if self.read() is not False:
            raise ValueError("Value of relay was not set to false.")


DriverFactory().register(driver_module=__name__, config=RelayConfig, factory=Relay)
