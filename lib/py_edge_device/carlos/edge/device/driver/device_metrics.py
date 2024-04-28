import psutil
from carlos.edge.interface.device import AnalogInput, DriverFactory
from carlos.edge.interface.device.driver_config import (
    DriverConfigWithDirection,
    DriverSignal,
)
from carlos.edge.interface.units import UnitOfMeasurement


class DeviceMetrics(AnalogInput):
    """Provides the metrics of the device."""

    _CPU_LOAD_SIGNAL_ID = "cpu.load_percent"
    _CPU_TEMP_SIGNAL_ID = "cpu.temperature"
    _MEMORY_USAGE_SIGNAL_ID = "memory.usage_percent"
    _DISK_USAGE_SIGNAL_ID = "disk.usage_percent"

    def __init__(self, config: DriverConfigWithDirection):

        super().__init__(config=config)

    def signals(self) -> list[DriverSignal]:
        """Returns the signals of the DHT sensor."""

        return [
            DriverSignal(
                signal_identifier=self._CPU_LOAD_SIGNAL_ID,
                unit_of_measurement=UnitOfMeasurement.PERCENTAGE,
            ),
            DriverSignal(
                signal_identifier=self._CPU_TEMP_SIGNAL_ID,
                unit_of_measurement=UnitOfMeasurement.CELSIUS,
            ),
            DriverSignal(
                signal_identifier=self._MEMORY_USAGE_SIGNAL_ID,
                unit_of_measurement=UnitOfMeasurement.PERCENTAGE,
            ),
            DriverSignal(
                signal_identifier=self._DISK_USAGE_SIGNAL_ID,
                unit_of_measurement=UnitOfMeasurement.PERCENTAGE,
            ),
        ]

    def setup(self):
        pass

    def read(self) -> dict[str, float]:
        """Reads the device metrics."""

        return {
            self._CPU_LOAD_SIGNAL_ID: psutil.cpu_percent(interval=1.0),
            self._CPU_TEMP_SIGNAL_ID: self._read_cpu_temp(),
            self._MEMORY_USAGE_SIGNAL_ID: psutil.virtual_memory().percent,
            self._DISK_USAGE_SIGNAL_ID: psutil.disk_usage("/").percent,
        }

    @staticmethod
    def _read_cpu_temp() -> float:
        """Reads the CPU temperature."""
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                return float(f.read().strip()) / 1000
        except FileNotFoundError:
            return 0.0


DriverFactory().register(
    driver_module=__name__, config=DriverConfigWithDirection, factory=DeviceMetrics
)
