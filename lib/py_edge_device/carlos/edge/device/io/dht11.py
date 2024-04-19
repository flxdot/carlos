from carlos.edge.interface.device import GpioConfig, IoFactory

from ._dhtxx import DHTXX, DhtConfig, DHTType


class DHT11(DHTXX):
    """DHT11 Temperature and Humidity Sensor."""

    def __init__(self, config: GpioConfig):

        super().__init__(config=config)

        self._dht_type = DHTType.DHT11


IoFactory().register(ptype=__name__, config=DhtConfig, factory=DHT11)
