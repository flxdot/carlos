from carlos.edge.interface.device import AnalogInput, GPIOConfig, peripheral_registry

from ._dhtxx import DHT, DHTType


class DHT11(AnalogInput):
    """DHT11 Temperature and Humidity Sensor."""

    def __init__(self, config: GPIOConfig):

        super().__init__(config=config)

        self._dht = DHT(dht_type=DHTType.DHT11, pin=config.pin)

    def read(self) -> dict[str, float]:
        """Reads the temperature and humidity."""

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




peripheral_registry.register(ptype=__name__, config=GPIOConfig, factory=DHT11)