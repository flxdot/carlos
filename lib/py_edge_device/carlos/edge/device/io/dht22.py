from carlos.edge.interface.device import GpioConfig, IoFactory

from ._dhtxx import DHTXX, DHTType


class DHT22(DHTXX):
    """DHT22 Temperature and Humidity Sensor."""

    def __init__(self, config: GpioConfig):

        super().__init__(config=config)

        self._dht_type = DHTType.DHT22


IoFactory().register(ptype=__name__, config=GpioConfig, factory=DHT22)
