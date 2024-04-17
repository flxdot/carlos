from enum import StrEnum


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
        self.pin = pin
        self.dht_type = dht_type

        # setup the GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT)

    @property
    def dht_type(self):
        return self._dht_type

    def _read(self):
        """Internal read method.

        :returns (humidity in %, temperature in °C)"""

        # Send Falling signal to trigger sensor output data
        # Wait for 20ms to collect 42 bytes data
        GPIO.setup(self.pin, GPIO.OUT)
        set_max_priority()

        GPIO.output(self.pin, GPIO.HIGH)
        sleep(0.2)

        GPIO.output(self.pin, GPIO.LOW)
        sleep(0.018)

        GPIO.setup(self.pin, GPIO.IN)

        # a short delay needed
        for i in range(10):
            pass

        # pullup by host 20-40 us
        count = 0
        while GPIO.input(self.pin):
            count += 1
            if count > self.MAX_CNT:
                # print("pullup by host 20-40us failed")
                set_default_priority()
                return None, "pullup by host 20-40us failed"

        pulse_cnt = [0] * (2 * self.PULSES_CNT)
        fix_crc = False
        for i in range(0, self.PULSES_CNT * 2, 2):
            while not GPIO.input(self.pin):
                pulse_cnt[i] += 1
                if pulse_cnt[i] > self.MAX_CNT:
                    # print("pulldown by DHT timeout %d" % i))
                    set_default_priority()
                    return None, "pulldown by DHT timeout {}".format(i)

            while GPIO.input(self.pin):
                pulse_cnt[i + 1] += 1
                if pulse_cnt[i + 1] > self.MAX_CNT:
                    # print("pullup by DHT timeout {}".format((i + 1)))
                    if i == (self.PULSES_CNT - 1) * 2:
                        # fix_crc = True
                        # break
                        pass
                    set_default_priority()
                    return None, "pullup by DHT timeout {}".format(i)

        # back to normal priority
        set_default_priority()

        total_cnt = 0
        for i in range(2, 2 * self.PULSES_CNT, 2):
            total_cnt += pulse_cnt[i]

        # Low level ( 50 us) average counter
        average_cnt = total_cnt / (self.PULSES_CNT - 1)
        # print("low level average loop = {}".format(average_cnt))

        data = ""
        for i in range(3, 2 * self.PULSES_CNT, 2):
            if pulse_cnt[i] > average_cnt:
                data += "1"
            else:
                data += "0"

        data0 = int(data[0:8], 2)
        data1 = int(data[8:16], 2)
        data2 = int(data[16:24], 2)
        data3 = int(data[24:32], 2)
        data4 = int(data[32:40], 2)

        if fix_crc and data4 != ((data0 + data1 + data2 + data3) & 0xFF):
            data4 = data4 ^ 0x01
            data = data[0 : self.PULSES_CNT - 2] + ("1" if data4 & 0x01 else "0")

        if data4 == ((data0 + data1 + data2 + data3) & 0xFF):
            if self._dht_type == DHTtype.DHT11:
                humi = int(data0)
                temp = int(data2)
            elif self._dht_type == DHTtype.DHT22:
                humi = float(int(data[0:16], 2) * 0.1)
                temp = float(int(data[17:32], 2) * 0.2 * (0.5 - int(data[16], 2)))
        else:
            # print("checksum error!")
            return None, "checksum error!"

        return humi, temp

    def read(self, retries=15):
        for i in range(retries):
            humi, temp = self._read()
            if humi is not None:
                break
        if humi is None:
            return self._last_humi, self._last_temp
        self._last_humi, self._last_temp = humi, temp
        return humi, temp

    def measure(self):
        """Performs a measurement and returns all available values in a dictionary.
        The keys() are the names of the measurement and the values the corresponding values.

        :return: dict
        """

        humi, temp = self.read()
        if humi == 0 and temp == 0:
            return {"humidity": None, "temperature": None}
        return {"humidity": float(humi), "temperature": float(temp)}
