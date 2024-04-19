from contextlib import nullcontext

import pytest
from pydantic import ValidationError

from .driver_config import DriverConfig, I2cDriverConfig

VALID_DRIVER_MODULE = __name__
"""For a driver module to be valid, it must be importable. Everything else
is checked else where."""


class TestDriverConfig:

    @pytest.mark.parametrize(
        "driver_module, expected",
        [
            pytest.param(VALID_DRIVER_MODULE, VALID_DRIVER_MODULE, id="valid module"),
            pytest.param("non_existing_module", ValueError, id="invalid module"),
        ],
    )
    def test_driver_module_validation(
        self, driver_module: str, expected: str | type[Exception]
    ):
        """This function ensures that the driver module is valid."""

        if isinstance(expected, str):
            context = nullcontext()
        else:
            context = pytest.raises(expected)

        with context:
            config = DriverConfig(
                identifier="does-not-matter", driver_module=driver_module
            )

            assert config.driver_module == expected


class TestI2cDriverConfig:

    @pytest.mark.parametrize(
        "address, expected",
        [
            pytest.param("0x03", "0x03", id="string: minimum address"),
            pytest.param("0x77", "0x77", id="string: maximum address"),
            pytest.param("0x00", ValidationError, id="string: below minimum address"),
            pytest.param("0x78", ValidationError, id="string: above maximum address"),
            pytest.param("1e", "0x1e", id="string: valid address without 0x"),
            pytest.param("0xij", ValidationError, id="string: invalid hex"),
            pytest.param("0x0A", "0x0a", id="string: upper case hex"),
            pytest.param(0x03, "0x03", id="int: minimum address"),
            pytest.param(0x77, "0x77", id="int: maximum address"),
            pytest.param(0x00, ValidationError, id="int: below minimum address"),
            pytest.param(0x78, ValidationError, id="int: above maximum address"),
        ],
    )
    def test_address_validation(
        self, address: str | int, expected: str | type[Exception]
    ):
        """This function ensures that the address is valid."""

        if isinstance(expected, str):
            context = nullcontext()
        else:
            context = pytest.raises(expected)

        with context:
            config = I2cDriverConfig(
                identifier="does-not-matter",
                driver_module=VALID_DRIVER_MODULE,
                direction="input",  # does not matter for this test
                address=address,
            )

            assert config.address == expected
            assert config.address_int == int(config.address, 16)
