import time
from typing import Literal

from carlos.edge.interface.device import (
    AnalogInput,
    DriverDirection,
    DriverFactory,
    I2cDriverConfig,
)
from loguru import logger
from pydantic import Field

from carlos.edge.device.driver._utils import crc8
from carlos.edge.device.protocol import I2C


class SHT30Config(I2cDriverConfig):

    direction: DriverDirection = Field(DriverDirection.INPUT)

    address: Literal["0x44", "0x45"] = Field("0x44")


class SHT30(AnalogInput):
    """Sensirion SHT30 sensor driver.

    Data sheet:
    https://sensirion.com/media/documents/213E6A3B/63A5A569/Datasheet_SHT3x_DIS.pdf
    """

    I2C_ADDRESSES = (0x44, 0x45)

    REG_MEASURE = 0x2C
    """Register to start measurement with clock stretching."""
    REG_DATA = 0x00
    """Register to read measurement data."""

    PARAM_HIGH_REPEATABLITY = 0x06
    """Marks the measurement as high repeatability."""

    def __init__(self, config: SHT30Config):
        if config.address_int not in SHT30.I2C_ADDRESSES:
            raise ValueError(
                f"The address of the SHT sensor must be 0x45. "
                f"Got {config.address} instead"
            )

        super().__init__(config=config)

        self._i2c: I2C | None = None

    def setup(self):
        self._i2c = I2C(address=self.config.address_int)

    def read(self) -> dict[str, float]:
        """Reads various light levels from the sensor."""

        read_delay_ms = 100
        humidity, temperature = self._get_measurement(
            read_delay_ms=read_delay_ms
        )
        return {
            "temperature": float(temperature),
            "humidity": float(humidity),
        }

    def _get_measurement(self, read_delay_ms: int = 100) -> tuple[float, float]:
        """Gets the measurement from the sensor.

        :return: The humidity and temperature.
        :raises ValueError: If the data CRC of the data does not match.
        """

        assert self._i2c is not None, "The sensor has not been set up."

        self._i2c.write8(
            register=SHT30.REG_MEASURE, value=SHT30.PARAM_HIGH_REPEATABLITY
        )

        time.sleep(read_delay_ms / 1000)

        # read 6 bytes:
        # MSB Temp, LSB Temp, CRC Temp,
        # MSB Humidity, LSB Humidity, CRC Humidity
        data = self._i2c.read_list(register=0x00, length=6)

        temp_data = data[0] << 8 | data[1]
        temp_crc = data[2]
        if not self._validate_data(data=bytes(data[:2]), crc=temp_crc):
            raise ValueError("Temperature data is invalid.")

        humidity_data = data[3] << 8 | data[4]
        humidity_crc = data[5]
        if not self._validate_data(data=bytes(data[3:5]), crc=humidity_crc):
            raise ValueError("Humidity data is invalid.")

        # 0xFFFF = 2^16 - 1
        temperature = -45 + 175 * temp_data / 0xFFFF
        humidity = 100 * humidity_data / 0xFFFF

        return humidity, temperature

    @staticmethod
    def _validate_data(data: bytes, crc: int) -> bool:
        """Validates the data read from the sensor."""

        if not data:
            return False

        # For details see chapter 4.12 - Table 20 in the data sheet.
        data_crc = crc8(data=data, crc_init=0xFF, crc_final_xor=0x00, polynomial=0x31)
        return data_crc == crc


DriverFactory().register(driver_module=__name__, config=SHT30Config, factory=SHT30)
