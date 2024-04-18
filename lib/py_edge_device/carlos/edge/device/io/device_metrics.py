import psutil
from carlos.edge.interface.device import AnalogInput, IoConfig, IoFactory


class DeviceMetrics(AnalogInput):
    """Provides the metrics of the device."""

    def __init__(self, config: IoConfig):

        super().__init__(config=config)

    def read(self) -> dict[str, float]:
        """Reads the device metrics."""

        return {
            "cpu.load_percent": psutil.cpu_percent(interval=1.0),
            "cpu.temperature": self._read_cpu_temp(),
            "memory.usage_percent": psutil.virtual_memory().percent,
            "disk.usage_percent": psutil.disk_usage("/").percent,
        }

    @staticmethod
    def _read_cpu_temp() -> float:
        """Reads the CPU temperature."""
        try:
            with open("/sys/class/thermal/thermal_zone0/temp") as f:
                return float(f.read().strip()) / 1000
        except FileNotFoundError:
            return 0.0


IoFactory().register(ptype=__name__, config=IoConfig, factory=DeviceMetrics)
