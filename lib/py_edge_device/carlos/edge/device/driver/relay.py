import time

from carlos.edge.interface.device import (
    DigitalInput,
    DigitalOutput,
    DriverDirection,
    DriverFactory,
    GpioDriverConfig,
)
from carlos.edge.interface.device.driver_config import DriverSignal
from carlos.edge.interface.units import UnitOfMeasurement
from pydantic import Field

from carlos.edge.device.protocol import GPIO


class RelayConfig(GpioDriverConfig):

    direction: DriverDirection = Field(DriverDirection.BIDIRECTIONAL)


class Relay(DigitalOutput, DigitalInput):
    """Relay."""

    _STATE_SIGNAL_ID = "state"

    def __init__(self, config: RelayConfig):
        super().__init__(config=config)

        self._state = False

    def signals(self) -> list[DriverSignal]:
        """Returns the signals of the DHT sensor."""

        return [
            DriverSignal(
                signal_identifier=self._STATE_SIGNAL_ID,
                unit_of_measurement=UnitOfMeasurement.UNIT_LESS,
            ),
        ]

    def setup(self):

        # HIGH means off, LOW means
        GPIO.setup(self.config.pin, GPIO.OUT, initial=not self._state)

    def set(self, value: bool):
        """Writes the value to the relay."""

        self._state = value

        GPIO.setup(self.config.pin, GPIO.OUT)
        # HIGH (1) means off, LOW (0) means on
        GPIO.output(self.config.pin, not value)

    def read(self) -> dict[str, bool]:
        """Reads the value of the relay."""

        return {self._STATE_SIGNAL_ID: self._state}

    def test(self):
        """Tests the relay by reading the value."""

        self.set(False)
        time.sleep(0.01)
        state = self.read()
        if state[self._STATE_SIGNAL_ID]:
            raise ValueError(f"Value of relay was not set to false. Got: {state}")

        self.set(True)
        time.sleep(1)
        state = self.read()
        if not state[self._STATE_SIGNAL_ID]:
            raise ValueError(f"Value of relay was not set to true. Got: {state}")

        self.set(False)
        time.sleep(0.01)
        state = self.read()
        if state[self._STATE_SIGNAL_ID]:
            raise ValueError(f"Value of relay was not set to false. Got: {state}")


DriverFactory().register(driver_module=__name__, config=RelayConfig, factory=Relay)
