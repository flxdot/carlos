__all__ = ["DHTXX", "DhtConfig", "DHTType"]

from abc import ABC
from enum import StrEnum
from time import sleep
from typing import Literal

from carlos.edge.interface.device import AnalogInput, GpioDriverConfig
from pydantic import Field

from carlos.edge.device.protocol import GPIO


class DhtConfig(GpioDriverConfig):
    """Configuration for a DHT sensor."""

    direction: Literal["input"] = Field("input")


class DHTType(StrEnum):
    DHT11 = "DHT11"
    DHT22 = "DHT22"


class DHT:
    """Code for Temperature & Humidity Sensor of Seeed Studio.

    Code is originally from, but modified to my needs:
    http://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/
    """

    PULSES_CNT = 41

    MAX_CNT = 320

    def __init__(self, dht_type: DHTType, pin: int):
        """

        :param dht_type: either DHTtype.DHT11 or DHTtype.22
        :param pin: gpio pin where the sensor is connected to
        """

        # store the pin and type
        self._pin = pin
        self._dht_type = dht_type

        GPIO.setup(self._pin, GPIO.OUT)

    def read(self) -> tuple[float, float]:
        """Internal read method.

        http://www.ocfreaks.com/basics-interfacing-dht11-dht22-humidity-temperature-sensor-mcu/

        :returns (humidity in %, temperature in °C)"""

        # Send Falling signal to trigger sensor output data
        # Wait for 20ms to collect 42 bytes data
        GPIO.setup(self._pin, GPIO.OUT)
        GPIO.output(self._pin, GPIO.HIGH)
        sleep(0.2)
        GPIO.output(self._pin, GPIO.LOW)
        sleep(0.018)

        GPIO.setup(self._pin, GPIO.IN)

        # a short delay needed
        for _ in range(10):
            pass

        # pullup by host 20-40 us
        count = 0
        while GPIO.input(self._pin):
            count += 1
            if count > self.MAX_CNT:
                raise RuntimeError("pullup by host 20-40us failed")

        pulse_cnt = [0] * (2 * self.PULSES_CNT)
        for pulse in range(0, self.PULSES_CNT * 2, 2):
            while not GPIO.input(self._pin):
                pulse_cnt[pulse] += 1
                if pulse_cnt[pulse] > self.MAX_CNT:
                    raise RuntimeError(f"pulldown by DHT timeout: {pulse}")

            while GPIO.input(self._pin):
                pulse_cnt[pulse + 1] += 1
                if pulse_cnt[pulse + 1] > self.MAX_CNT:
                    if pulse == (self.PULSES_CNT - 1) * 2:
                        pass
                    raise RuntimeError(f"pullup by DHT timeout: {pulse}")

        total_cnt = 0
        for pulse in range(2, 2 * self.PULSES_CNT, 2):
            total_cnt += pulse_cnt[pulse]

        # Low level (50 us) average counter
        average_cnt = total_cnt / (self.PULSES_CNT - 1)

        data = ""
        for pulse in range(3, 2 * self.PULSES_CNT, 2):
            if pulse_cnt[pulse] > average_cnt:
                data += "1"
            else:
                data += "0"

        byte0 = int(data[0:8], 2)
        byte1 = int(data[8:16], 2)
        byte2 = int(data[16:24], 2)
        byte3 = int(data[24:32], 2)
        crc_byte = int(data[32:40], 2)

        data_checksum = (byte0 + byte1 + byte2 + byte3) & 0xFF
        if crc_byte != data_checksum:
            raise RuntimeError("checksum error!")

        if self._dht_type == DHTType.DHT11:
            humidity = float(byte0)
            temperature = float(byte2)
        else:
            humidity = float(int(data[0:16], 2) * 0.1)
            temperature = float(int(data[17:32], 2) * 0.2 * (0.5 - int(data[16], 2)))

        return temperature, humidity


class DHTXX(AnalogInput, ABC):
    """DHTXX Temperature and Humidity Sensor."""

    def __init__(self, config: GpioDriverConfig):

        super().__init__(config=config)

        self._dht: DHT | None = None
        self._dht_type: DHTType | None = None

    def setup(self):
        """Sets up the DHT11 sensor."""

        self._dht = DHT(dht_type=self._dht_type, pin=self.config.pin)

    def read(self) -> dict[str, float]:
        """Reads the temperature and humidity."""

        assert self._dht is not None, "The DHT sensor has not been initialized."

        # Reading the DHT sensor is quite unreliable, as the device is not a real-time
        # device. Thus, we just try it a couple of times and fail if it does not work.
        last_error: Exception | None = None
        for i in range(16):
            try:
                temperature, humidity = self._dht.read()
                return {
                    "temperature": temperature,
                    "humidity": humidity,
                }
            except RuntimeError as ex:
                last_error = ex

        assert last_error is not None
        raise last_error