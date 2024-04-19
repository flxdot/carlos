from carlos.edge.interface.device import DriverFactory, GpioDriverConfig

from ._dhtxx import DHTXX, DhtConfig, DHTType


class DHT22(DHTXX):
    """DHT22 Temperature and Humidity Sensor."""

    def __init__(self, config: GpioDriverConfig):

        super().__init__(config=config)

        self._dht_type = DHTType.DHT22


DriverFactory().register(driver_module=__name__, config=DhtConfig, factory=DHT22)
