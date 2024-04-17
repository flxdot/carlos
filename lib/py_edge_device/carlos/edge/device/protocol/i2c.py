#!/usr/bin/python

import re
from threading import RLock
from typing import Sequence

import smbus2


class i2cLock:
    """Use this i2c lock to prevent simultaneous access of the i2c bus by different
    threads."""

    instance = None

    def __new__(cls):
        if not i2cLock.instance:
            i2cLock.instance = RLock()
        return i2cLock.instance


class I2C:
    """This class is based on, but heavily modified from, the Adafruit_I2C class"""

    def __init__(self, address: int, bus: int | None = None):
        """Creates an instance of the I2C class.

        :param address: The I2C address of the device.
        :param bus: The I2C bus number. If None, the bus number is auto-detected.
        """

        self.address = address
        # By default, the correct I2C bus is auto-detected using /proc/cpuinfo
        # Alternatively, you can hard-code the bus version below:
        # self.bus = smbus2.SMBus(0); # Force I2C0 (early 256MB Pi's)
        # self.bus = smbus2.SMBus(1); # Force I2C1 (512MB Pi's)
        self.bus = smbus2.SMBus(
            bus=bus if bus is not None else I2C.get_pi_i2v_bus_number()
        )

    def write8(self, register: int, value: int):
        """Writes an 8-bit value to the specified register/address"""
        try:
            self.bus.write_byte_data(
                i2c_addr=self.address, register=register, value=value
            )
        except IOError:
            raise IOError(
                f"Error accessing 0x{self.address:0x}: Check your I2C address."
            )

    def write16(self, register: int, value: int):
        """Writes a 16-bit value to the specified register/address pair"""
        try:
            self.bus.write_word_data(
                i2c_addr=self.address, register=register, value=value
            )
        except IOError:
            raise IOError(
                f"Error accessing 0x{self.address:0x}: Check your I2C address."
            )

    def write_raw8(self, value: int):
        """Writes an 8-bit value on the bus"""
        try:
            self.bus.write_byte(i2c_addr=self.address, value=value)
        except IOError:
            raise IOError(
                f"Error accessing 0x{self.address:0x}: Check your I2C address."
            )

    def write_list(self, register: int, data: Sequence[int]):
        """Writes an array of bytes using I2C format"""
        try:
            self.bus.write_i2c_block_data(
                i2c_addr=self.address, register=register, data=data
            )
        except IOError:
            raise IOError(
                f"Error accessing 0x{self.address:0x}: Check your I2C address."
            )

    def read_list(self, register: int, length: int):
        """Read a list of bytes from the I2C device"""
        try:
            return self.bus.read_i2c_block_data(
                i2c_addr=self.address, register=register, length=length
            )
        except IOError:
            raise IOError(
                f"Error accessing 0x{self.address:0x}: Check your I2C address."
            )

    def read_uint8(self, register: int):
        """Read an unsigned byte from the I2C device"""
        try:
            return self.bus.read_byte_data(i2c_addr=self.address, register=register)
        except IOError:
            raise IOError(
                f"Error accessing 0x{self.address:0x}: Check your I2C address."
            )

    def read_int8(self, register: int):
        """Reads a signed byte from the I2C device"""
        result = self.read_uint8(register=register)
        if result > 127:
            result -= 256
        return result

    def read_uint16(self, register: int, little_endian: bool = True):
        """Reads an unsigned 16-bit value from the I2C device"""
        try:
            result = self.bus.read_word_data(i2c_addr=self.address, register=register)
            # Swap bytes if using big endian because read_word_data assumes little
            # endian on ARM (little endian) systems.
            if not little_endian:
                result = ((result << 8) & 0xFF00) + (result >> 8)
            return result
        except IOError:
            raise IOError(
                f"Error accessing 0x{self.address:0x}: Check your I2C address."
            )

    def read_int16(self, register: int, little_endian=True):
        """Reads a signed 16-bit value from the I2C device"""
        result = self.read_uint16(register=register, little_endian=little_endian)
        if result > 32767:
            result -= 65536
        return result

    @staticmethod
    def get_pi_revision() -> int:
        """Gets the version number of the Raspberry Pi board"""
        # Revision list available at:
        # http://elinux.org/RPi_HardwareHistory#Board_Revision_History
        try:
            with open("/proc/cpuinfo", "r") as infile:
                for line in infile:
                    # Match a line of the form "Revision : 0002" while ignoring extra
                    # info in front of the revsion
                    # (like 1000 when the Pi was over-volted).
                    match = re.match("Revision\s+:\s+.*(\w{4})$", line)
                    if match and match.group(1) in ["0000", "0002", "0003"]:
                        # Return revision 1 if revision ends with 0000, 0002 or 0003.
                        return 1
                    elif match:
                        # Assume revision 2 if revision ends with any other 4 chars.
                        return 2
                # Couldn't find the revision, assume revision 0 like older code for
                # compatibility.
                return 0
        except:
            return 0

    @staticmethod
    def get_pi_i2v_bus_number() -> int:
        # Gets the I2C bus number /dev/i2c#
        return 1 if I2C.get_pi_revision() > 1 else 0
