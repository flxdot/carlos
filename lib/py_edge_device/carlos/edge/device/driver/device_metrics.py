import psutil
from carlos.edge.interface.device import AnalogInput, DriverConfig, DriverFactory


class DeviceMetrics(AnalogInput):
    """Provides the metrics of the device."""

    def __init__(self, config: DriverConfig):

        super().__init__(config=config)

    def setup(self):
        pass

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


DriverFactory().register(driver_module=__name__, config=DriverConfig,
                         factory=DeviceMetrics)
