import time
from typing import Literal

from carlos.edge.interface.device import AnalogInput, DriverFactory, I2cDriverConfig
from pydantic import Field

from carlos.edge.device.protocol import I2C


class Si1145Config(I2cDriverConfig):

    direction: Literal["input"] = Field("input")

    address: Literal["0x60"] = Field("0x60")


class SI1145(AnalogInput):

    def __init__(self, config: Si1145Config):

        if config.address_int != SDL_Pi_SI1145.ADDR:
            raise ValueError(
                f"The address of the SI1145 sensor must be 0x60. Got {config.address} instead"
            )

        super().__init__(config=config)

        self._si1145: SDL_Pi_SI1145 | None = None

    def setup(self):

        self._si1145 = SDL_Pi_SI1145()

    def read(self) -> dict[str, float]:
        """Reads various light levels from the sensor."""

        assert self._si1145 is not None, "The sensor has not been set up."

        vis_raw = self._si1145.read_visible()
        vis_lux = self._si1145.convert_visible_to_lux(vis_raw)
        ir_raw = self._si1145.read_ir()
        ir_lux = self._si1145.convert_ir_to_lux(ir_raw)
        uv_idx = self._si1145.read_uv_index()

        return {
            "visual-light-raw": float(vis_raw),
            "visual-light": float(vis_lux),
            "infrared-light-raw": float(ir_raw),
            "infrared-light": float(ir_lux),
            "uv-index": float(uv_idx),
        }


DriverFactory().register(driver_module=__name__, config=Si1145Config, factory=SI1145)


class SDL_Pi_SI1145:
    """Interface to the SI1145 UV Light Sensor by Adafruit.

    Note: This sensor has a static I2C Address of 0x60.

    https://www.silabs.com/documents/public/data-sheets/Si1145-46-47.pdf

    Modified for medium range vis, IR SDL December 2016 and
    non Adafruit I2C (interfers with others)

    Original Author: Joe Gutting

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
    """

    # COMMANDS
    PARAM_QUERY = 0x80
    PARAM_SET = 0xA0
    NOP = 0x0
    RESET = 0x01
    BUSADDR = 0x02
    PS_FORCE = 0x05
    ALS_FORCE = 0x06
    PSALS_FORCE = 0x07
    PS_PAUSE = 0x09
    ALS_PAUSE = 0x0A
    PSALS_PAUSE = 0xB
    PS_AUTO = 0x0D
    ALS_AUTO = 0x0E
    PSALS_AUTO = 0x0F
    GET_CAL = 0x12

    # Parameters
    PARAM_I2CADDR = 0x00
    PARAM_CHLIST = 0x01
    PARAM_CHLIST_ENUV = 0x80
    PARAM_CHLIST_ENAUX = 0x40
    PARAM_CHLIST_ENALSIR = 0x20
    PARAM_CHLIST_ENALSVIS = 0x10
    PARAM_CHLIST_ENPS1 = 0x01
    PARAM_CHLIST_ENPS2 = 0x02
    PARAM_CHLIST_ENPS3 = 0x04

    PARAM_PSLED12SEL = 0x02
    PARAM_PSLED12SEL_PS2NONE = 0x00
    PARAM_PSLED12SEL_PS2LED1 = 0x10
    PARAM_PSLED12SEL_PS2LED2 = 0x20
    PARAM_PSLED12SEL_PS2LED3 = 0x40
    PARAM_PSLED12SEL_PS1NONE = 0x00
    PARAM_PSLED12SEL_PS1LED1 = 0x01
    PARAM_PSLED12SEL_PS1LED2 = 0x02
    PARAM_PSLED12SEL_PS1LED3 = 0x04

    PARAM_PSLED3SEL = 0x03
    PARAM_PSENCODE = 0x05
    PARAM_ALSENCODE = 0x06

    PARAM_PS1ADCMUX = 0x07
    PARAM_PS2ADCMUX = 0x08
    PARAM_PS3ADCMUX = 0x09
    PARAM_PSADCOUNTER = 0x0A
    PARAM_PSADCGAIN = 0x0B
    PARAM_PSADCMISC = 0x0C
    PARAM_PSADCMISC_RANGE = 0x20
    PARAM_PSADCMISC_PSMODE = 0x04

    PARAM_ALSIRADCMUX = 0x0E
    PARAM_AUXADCMUX = 0x0F

    PARAM_ALS_VIS_ADC_COUNTER = 0x10
    PARAM_ALS_VIS_ADC_GAIN = 0x11
    PARAM_ALS_VIS_ADC_MISC = 0x12
    PARAM_ALS_VIS_ADC_MISC_VISRANGE = 0x10
    # PARAM_ALS_VIS_ADC_MISC_VISRANGE = 0x00

    PARAM_ALS_IR_ADC_COUNTER = 0x1D
    PARAM_ALS_IR_ADC_GAIN = 0x1E
    PARAM_ALS_IR_ADC_MISC = 0x1F
    PARAM_ALS_IR_ADC_MISC_RANGE = 0x20
    # PARAM_ALS_IR_ADC_MISC_RANGE = 0x00

    PARAM_ADCCOUNTER_511CLK = 0x70

    PARAM_ADCMUX_SMALLIR = 0x00
    PARAM_ADCMUX_LARGEIR = 0x03

    # REGISTERS
    REG_PARTID = 0x00
    REG_REVID = 0x01
    REG_SEQID = 0x02

    REG_INTCFG = 0x03
    REG_INTCFG_INTOE = 0x01
    REG_INTCFG_INTMODE = 0x02

    REG_IRQEN = 0x04
    REG_IRQEN_ALSEVERYSAMPLE = 0x01
    REG_IRQEN_PS1EVERYSAMPLE = 0x04
    REG_IRQEN_PS2EVERYSAMPLE = 0x08
    REG_IRQEN_PS3EVERYSAMPLE = 0x10

    REG_IRQMODE1 = 0x05
    REG_IRQMODE2 = 0x06

    REG_HWKEY = 0x07
    REG_MEASRATE0 = 0x08
    REG_MEASRATE1 = 0x09
    REG_PSRATE = 0x0A
    REG_PSLED21 = 0x0F
    REG_PSLED3 = 0x10
    REG_UCOEFF0 = 0x13
    REG_UCOEFF1 = 0x14
    REG_UCOEFF2 = 0x15
    REG_UCOEFF3 = 0x16
    REG_PARAMWR = 0x17
    REG_COMMAND = 0x18
    REG_RESPONSE = 0x20
    REG_IRQSTAT = 0x21
    REG_IRQSTAT_ALS = 0x01

    REG_ALSVISDATA0 = 0x22
    REG_ALSVISDATA1 = 0x23
    REG_ALSIRDATA0 = 0x24
    REG_ALSIRDATA1 = 0x25
    REG_PS1DATA0 = 0x26
    REG_PS1DATA1 = 0x27
    REG_PS2DATA0 = 0x28
    REG_PS2DATA1 = 0x29
    REG_PS3DATA0 = 0x2A
    REG_PS3DATA1 = 0x2B
    REG_UVINDEX0 = 0x2C
    REG_UVINDEX1 = 0x2D
    REG_PARAMRD = 0x2E
    REG_CHIPSTAT = 0x30

    # I2C Address
    ADDR = 0x60

    DARK_OFFSET_VIS = 259
    DARK_OFFSE_TIR = 253

    def __init__(self):
        """Constructor."""

        self._i2c = I2C(address=SDL_Pi_SI1145.ADDR)

        self._reset()
        self._load_calibration()

    # device reset
    def _reset(self):
        """Resets the device

        :return:
        """

        with self._i2c.lock:
            self._i2c.write8(register=SDL_Pi_SI1145.REG_MEASRATE0, value=0x00)
            self._i2c.write8(register=SDL_Pi_SI1145.REG_MEASRATE1, value=0x00)
            self._i2c.write8(register=SDL_Pi_SI1145.REG_IRQEN, value=0x00)
            self._i2c.write8(register=SDL_Pi_SI1145.REG_IRQMODE1, value=0x00)
            self._i2c.write8(register=SDL_Pi_SI1145.REG_IRQMODE2, value=0x00)
            self._i2c.write8(register=SDL_Pi_SI1145.REG_INTCFG, value=0x00)
            self._i2c.write8(register=SDL_Pi_SI1145.REG_IRQSTAT, value=0xFF)

            self._i2c.write8(
                register=SDL_Pi_SI1145.REG_COMMAND, value=SDL_Pi_SI1145.RESET
            )
            time.sleep(0.01)
            self._i2c.write8(register=SDL_Pi_SI1145.REG_HWKEY, value=0x17)
            time.sleep(0.01)

    def write_param(self, parameter: int, value: int) -> int:
        """Write Parameter to the Sensor."""

        with self._i2c.lock:
            self._i2c.write8(register=SDL_Pi_SI1145.REG_PARAMWR, value=value)
            self._i2c.write8(
                register=SDL_Pi_SI1145.REG_COMMAND,
                value=parameter | SDL_Pi_SI1145.PARAM_SET,
            )
            param_val = self._i2c.read_uint8(register=SDL_Pi_SI1145.REG_PARAMRD)
        return param_val

    def read_param(self, parameter: int) -> int:
        """Read Parameter from the Sensor."""

        with self._i2c.lock:
            self._i2c.write8(
                register=SDL_Pi_SI1145.REG_COMMAND,
                value=parameter | SDL_Pi_SI1145.PARAM_QUERY,
            )
            return self._i2c.read_uint8(register=SDL_Pi_SI1145.REG_PARAMRD)

    # load calibration to sensor
    def _load_calibration(self):
        """Load calibration data."""

        with self._i2c.lock:
            # Enable UVindex measurement coefficients!
            self._i2c.write8(register=SDL_Pi_SI1145.REG_UCOEFF0, value=0x29)
            self._i2c.write8(register=SDL_Pi_SI1145.REG_UCOEFF1, value=0x89)
            self._i2c.write8(register=SDL_Pi_SI1145.REG_UCOEFF2, value=0x02)
            self._i2c.write8(register=SDL_Pi_SI1145.REG_UCOEFF3, value=0x00)

            # Enable UV sensor
            self.write_param(
                parameter=SDL_Pi_SI1145.PARAM_CHLIST,
                value=SDL_Pi_SI1145.PARAM_CHLIST_ENUV
                | SDL_Pi_SI1145.PARAM_CHLIST_ENALSIR
                | SDL_Pi_SI1145.PARAM_CHLIST_ENALSVIS
                | SDL_Pi_SI1145.PARAM_CHLIST_ENPS1,
            )

            # Enable interrupt on every sample
            self._i2c.write8(
                register=SDL_Pi_SI1145.REG_INTCFG,
                value=SDL_Pi_SI1145.REG_INTCFG_INTOE,
            )
            self._i2c.write8(
                register=SDL_Pi_SI1145.REG_IRQEN,
                value=SDL_Pi_SI1145.REG_IRQEN_ALSEVERYSAMPLE,
            )

            # /****************************** Prox Sense 1 */

            # Program LED current
            self._i2c.write8(
                register=SDL_Pi_SI1145.REG_PSLED21, value=0x03
            )  # 20mA for LED 1 only
            self.write_param(
                parameter=SDL_Pi_SI1145.PARAM_PS1ADCMUX,
                value=SDL_Pi_SI1145.PARAM_ADCMUX_LARGEIR,
            )

            # Prox sensor #1 uses LED #1
            self.write_param(
                parameter=SDL_Pi_SI1145.PARAM_PSLED12SEL,
                value=SDL_Pi_SI1145.PARAM_PSLED12SEL_PS1LED1,
            )

            # Fastest clocks, clock div 1
            self.write_param(parameter=SDL_Pi_SI1145.PARAM_PSADCGAIN, value=0x00)

            # Take 511 clocks to measure
            self.write_param(
                parameter=SDL_Pi_SI1145.PARAM_PSADCOUNTER,
                value=SDL_Pi_SI1145.PARAM_ADCCOUNTER_511CLK,
            )

            # in prox mode, high range
            self.write_param(
                parameter=SDL_Pi_SI1145.PARAM_PSADCMISC,
                value=SDL_Pi_SI1145.PARAM_PSADCMISC_RANGE
                | SDL_Pi_SI1145.PARAM_PSADCMISC_PSMODE,
            )
            self.write_param(
                parameter=SDL_Pi_SI1145.PARAM_ALSIRADCMUX,
                value=SDL_Pi_SI1145.PARAM_ADCMUX_SMALLIR,
            )

            # Fastest clocks, clock div 1
            self.write_param(
                parameter=SDL_Pi_SI1145.PARAM_ALS_IR_ADC_GAIN,
                value=0,
                # value=4
            )

            # Take 511 clocks to measure
            self.write_param(
                parameter=SDL_Pi_SI1145.PARAM_ALS_IR_ADC_COUNTER,
                value=SDL_Pi_SI1145.PARAM_ADCCOUNTER_511CLK,
            )

            # in high range mode
            self.write_param(
                parameter=SDL_Pi_SI1145.PARAM_ALS_IR_ADC_MISC,
                value=0,
                # value=SDL_Pi_SI1145.PARAM_ALS_IR_ADC_MISC_RANGE
            )

            # fastest clocks, clock div 1
            self.write_param(
                parameter=SDL_Pi_SI1145.PARAM_ALS_VIS_ADC_GAIN,
                value=0,
                # value=4
            )

            # Take 511 clocks to measure
            self.write_param(
                parameter=SDL_Pi_SI1145.PARAM_ALS_VIS_ADC_COUNTER,
                value=SDL_Pi_SI1145.PARAM_ADCCOUNTER_511CLK,
            )

            # in high range mode (not normal signal)
            self.write_param(
                parameter=SDL_Pi_SI1145.PARAM_ALS_VIS_ADC_MISC,
                value=0,
                # value=SDL_Pi_SI1145.PARAM_ALS_VIS_ADC_MISC_VISRANGE
            )

            # measurement rate for auto
            self._i2c.write8(
                register=SDL_Pi_SI1145.REG_MEASRATE0, value=0xFF
            )  # 255 * 31.25uS = 8ms

            # auto run
            self._i2c.write8(
                register=SDL_Pi_SI1145.REG_COMMAND, value=SDL_Pi_SI1145.PSALS_AUTO
            )

    def read_visible(self) -> int:
        """returns visible + IR light levels"""

        with self._i2c.lock:
            return self._i2c.read_uint16(register=SDL_Pi_SI1145.REG_ALSVISDATA0)

    def read_visible_lux(self) -> float:
        """returns visible + IR light levels in lux"""

        return self.convert_visible_to_lux(self.read_visible())

    def read_ir(self) -> int:
        """returns IR light levels"""

        with self._i2c.lock:
            return self._i2c.read_uint16(register=SDL_Pi_SI1145.REG_ALSIRDATA0)

    def read_ir_lux(self) -> float:
        """returns IR light levels in lux"""

        return self.convert_ir_to_lux(self.read_ir())

    def read_prox(self) -> int:
        """Returns "Proximity" - assumes an IR LED is attached to LED"""

        with self._i2c.lock:
            return self._i2c.read_uint16(register=SDL_Pi_SI1145.REG_PS1DATA0)

    def read_uv(self) -> int:
        """Returns the UV index * 100 (divide by 100 to get the index)"""

        with self._i2c.lock:
            # apply additional calibration of /10 based on sunlight
            return self._i2c.read_uint16(register=SDL_Pi_SI1145.REG_UVINDEX0) / 10

    def read_uv_index(self) -> float:
        """Returns the UV Index."""

        return self.read_uv() / 100

    def convert_ir_to_lux(self, ir: int) -> float:
        """Converts IR levels to lux."""

        return self._convert_raw_to_lux(
            raw=ir,
            dark_offset=SDL_Pi_SI1145.DARK_OFFSE_TIR,
            calibration_factor=50,  # calibration factor to sunlight applied
            param_adc_gain=SDL_Pi_SI1145.PARAM_ALS_IR_ADC_GAIN,
            param_adc_misc=SDL_Pi_SI1145.PARAM_ALS_IR_ADC_MISC,
        )

    @staticmethod
    def convert_uv_to_index(uv: int) -> float:
        """Converts the read UV values to UV index."""

        return uv / 100

    def convert_visible_to_lux(self, vis: int) -> float:
        """Converts the visible light level to lux."""

        # Param 1: ALS_VIS_ADC_MISC
        return self._convert_raw_to_lux(
            raw=vis,
            dark_offset=SDL_Pi_SI1145.DARK_OFFSET_VIS,
            calibration_factor=100,  # calibration to bright sunlight added
            param_adc_gain=SDL_Pi_SI1145.PARAM_ALS_VIS_ADC_GAIN,
            param_adc_misc=SDL_Pi_SI1145.PARAM_ALS_VIS_ADC_MISC,
        )

    def _convert_raw_to_lux(
        self,
        raw: int,
        dark_offset: int,
        calibration_factor: int,
        param_adc_gain: int,
        param_adc_misc: int,
    ) -> float:
        """Converts a raw input to Lux by applying a dark offset and a calibration
        factor."""

        raw = raw - dark_offset
        if raw < 0:
            raw = 0

        lux = 2.44

        # Get gain
        gain = 1
        # These are set to defaults in the Adafruit driver_module -
        # need to change if you change them in the SI1145 driver_module
        # range_ = self.read_param(parameter=adc_misc)
        # if (range_ & 32) == 32:
        #     gain = 14.5

        # Get sensitivity
        multiplier = 1
        # These are set to defaults in the Adafruit driver_module -
        # need to change if you change them in the SI1145 driver_module
        # sensitivity = self.read_param(parameter=adc_gain)
        # if (sensitivity & 7) == 0:
        #     multiplier = 1
        # if (sensitivity & 7) == 1:
        #     multiplier = 2
        # if (sensitivity & 7) == 2:
        #     multiplier = 4
        # if (sensitivity & 7) == 3:
        #     multiplier = 8
        # if (sensitivity & 7) == 4:
        #     multiplier = 16
        # if (sensitivity & 7) == 5:
        #     multiplier = 32
        # if (sensitivity & 7) == 6:
        #     multiplier = 64
        # if (sensitivity & 7) == 7:
        #     multiplier = 128

        return raw * (gain / (lux * multiplier)) * calibration_factor
