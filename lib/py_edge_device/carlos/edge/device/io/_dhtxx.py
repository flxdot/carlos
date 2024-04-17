from enum import StrEnum
from time import sleep

from carlos.edge.device.protocol import GPIO


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

        # setup the GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self._pin, GPIO.OUT)

    def read(self) -> tuple[int | float, int | float]:
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

        data_checksum = ((byte0 + byte1 + byte2 + byte3) & 0xFF)
        if crc_byte != data_checksum:
            raise RuntimeError("checksum error!")

        if self._dht_type == DHTType.DHT11:
            humidity = byte0
            temperature = byte2
        else:
            humidity = float(int(data[0:16], 2) * 0.1)
            temperature = float(int(data[17:32], 2) * 0.2 * (0.5 - int(data[16], 2)))

        return humidity, temperature
