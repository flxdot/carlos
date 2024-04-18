from carlos.edge.interface.device import AnalogInput, GpioConfig, IoFactory

from ._dhtxx import DHT, DHTType


class DHT11(AnalogInput):
    """DHT11 Temperature and Humidity Sensor."""

    def __init__(self, config: GpioConfig):

        super().__init__(config=config)

        self._dht: DHT | None = None

    def setup(self):
        """Sets up the DHT11 sensor."""

        self._dht = DHT(dht_type=DHTType.DHT11, pin=self.config.pin)

    def read(self) -> dict[str, float]:
        """Reads the temperature and humidity."""

        assert self._dht is not None, "The DHT sensor has not been initialized."

        # Reading the DHT sensor is quite unreliable, as the device is not a real-time
        # device. Thus, we just try it a couple of times and fail if it does not work.
        for i in range(16):
            try:
                temperature, humidity = self._dht.read()
                return {
                    "temperature": temperature,
                    "humidity": humidity,
                }
            except RuntimeError:
                pass

        raise RuntimeError("Could not read DHT11 sensor.")


IoFactory().register(ptype=__name__, config=GpioConfig, factory=DHT11)
