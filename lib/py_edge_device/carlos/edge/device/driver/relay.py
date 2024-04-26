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
        # HIGH (1) means off, LOW (0) means on
        GPIO.output(self.config.pin, not value)

    def read(self) -> dict[str, bool]:
        """Reads the value of the relay."""

        GPIO.setup(self.config.pin, GPIO.IN)
        # HIGH (1) means off, LOW (0) means on
        return {"state": not GPIO.input(self.config.pin)}

    def test(self):
        """Tests the relay by reading the value."""

        self.set(False)
        time.sleep(0.01)
        state = self.read()
        if state is not False:
            raise ValueError(f"Value of relay was not set to false. Got: {state}")

        self.set(True)
        time.sleep(1)
        state = self.read()
        if state is not True:
            raise ValueError(f"Value of relay was not set to true. Got: {state}")

        self.set(False)
        time.sleep(0.01)
        state = self.read()
        if state is not False:
            raise ValueError(f"Value of relay was not set to false. Got: {state}")


DriverFactory().register(driver_module=__name__, config=RelayConfig, factory=Relay)
