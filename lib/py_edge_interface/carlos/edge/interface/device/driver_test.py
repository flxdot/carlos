from contextlib import nullcontext
from secrets import token_hex
from typing import Self

import pytest
from pydantic import BaseModel

from ..units import UnitOfMeasurement
from .driver import (
    AnalogInput,
    CarlosDriver,
    DigitalOutput,
    DriverFactory,
    validate_device_address_space,
)
from .driver_config import (
    DriverDirection,
    DriverSignal,
    GpioDriverConfig,
    I2cDriverConfig,
)

DRIVER_MODULE = __name__

ANALOG_INPUT_VALUE = {"value": 0.0}
ANALOG_INPUT_CONFIG = GpioDriverConfig(
    identifier="analog-input-test",
    driver_module=DRIVER_MODULE,
    direction="input",
    pin=13,
)
DIGITAL_OUTPUT_CONFIG = GpioDriverConfig(
    identifier="digital-output-test",
    driver_module=DRIVER_MODULE,
    direction="output",
    pin=14,
)


class AnalogInputTest(AnalogInput):

    def signals(self) -> list[DriverSignal]:
        return [
            DriverSignal(
                signal_identifier=key, unit_of_measurement=UnitOfMeasurement.UNIT_LESS
            )
            for key in ANALOG_INPUT_VALUE.keys()
        ]

    def setup(self):
        pass

    def read(self) -> dict[str, float]:
        return ANALOG_INPUT_VALUE


def test_carlos_driver_base():
    """This test tests the methods of the CarlosDriverBase class via the
    AnalogInputTest class."""

    driver = AnalogInputTest(config=ANALOG_INPUT_CONFIG)

    assert isinstance(str(driver), str), "Could not convert driver to string."
    assert (
        driver.identifier == ANALOG_INPUT_CONFIG.identifier
    ), "Identifier should be the same as in the config."


def test_analog_input():
    """This test tests the AnalogInput Interface bia the AnalogInputTest class."""
    analog_input = AnalogInputTest(config=ANALOG_INPUT_CONFIG)

    assert analog_input.direction == DriverDirection.INPUT, "Direction should be INPUT."

    assert (
        analog_input.test() == ANALOG_INPUT_VALUE
    ), "Test function should return a reading."

    # using output config for input should raise an error
    with pytest.raises(ValueError):
        AnalogInputTest(config=DIGITAL_OUTPUT_CONFIG)


@pytest.mark.asyncio
async def test_async_analog_input():
    """This test tests the AnalogInput Interface bia the AnalogInputTest class."""
    analog_input = AnalogInputTest(config=ANALOG_INPUT_CONFIG)

    assert (
        await analog_input.read_async() == ANALOG_INPUT_VALUE
    ), "Test function should return a reading."


class DigitalOutputTest(DigitalOutput):

    def signals(self) -> list[DriverSignal]:
        return [
            DriverSignal(
                signal_identifier="state",
                unit_of_measurement=UnitOfMeasurement.UNIT_LESS,
            )
        ]

    def setup(self) -> Self:
        self.pytest_state = None
        return self

    def read(self) -> dict[str, float]:
        return {"state": self.pytest_state}

    def set(self, value: bool):
        self.pytest_state = value


def test_digital_output():
    """This test tests the DigitalOutput Interface via the DigitalOutputTest class."""
    digital_output = DigitalOutputTest(config=DIGITAL_OUTPUT_CONFIG).setup()

    assert (
        digital_output.direction == DriverDirection.OUTPUT
    ), "Direction should be OUTPUT."

    assert digital_output.read()["state"] is None, "Initial state should be None."

    digital_output.test()

    assert (
        digital_output.read()["state"] is not None
    ), "State should be set to a value after running the test."

    # using input config for output should raise an error
    with pytest.raises(ValueError):
        DigitalOutputTest(config=ANALOG_INPUT_CONFIG)


@pytest.mark.asyncio
async def test_async_digital_output():
    """This test tests the async DigitalOutput Interface bia the
    DigitalOutputTest class."""
    digital_output = DigitalOutputTest(config=DIGITAL_OUTPUT_CONFIG).setup()

    assert digital_output.pytest_state is None, "Initial state should be None."

    await digital_output.set_async(True)

    assert digital_output.pytest_state is True, "State should be set to True."

    await digital_output.set_async(False)

    assert digital_output.pytest_state is False, "State should be set to False."


def test_driver_factory():
    """This test tests the driver factory function."""

    factory = DriverFactory()

    raw_analog_input_config = ANALOG_INPUT_CONFIG.model_dump(mode="json")

    # Sofar the AnalogInputTest class was never registered, thus the build method
    # should raise a RuntimeError.
    with pytest.raises(RuntimeError):
        factory.build(raw_analog_input_config)

    factory.register(
        driver_module=DRIVER_MODULE, config=GpioDriverConfig, factory=AnalogInputTest
    )

    # Trying to register a driver with the same driver_module should raise a
    # RuntimeError.
    with pytest.raises(RuntimeError):
        factory.register(
            driver_module=DRIVER_MODULE,
            config=GpioDriverConfig,
            factory=AnalogInputTest,
        )

    # Passing a non DriverConfig type as config should raise a ValueError.
    with pytest.raises(ValueError):
        factory.register(
            driver_module=DRIVER_MODULE + ".test",
            config=BaseModel,
            factory=DigitalOutputTest,
        )

    driver = factory.build(raw_analog_input_config)
    assert isinstance(
        driver, AnalogInputTest
    ), "Driver should be an instance of AnalogInputTest."
    assert isinstance(
        driver.config, GpioDriverConfig
    ), "Config should be an instance of GpioDriverConfig."


@pytest.mark.parametrize(
    "drivers, expected_exception",
    [
        pytest.param([AnalogInputTest(ANALOG_INPUT_CONFIG)], None, id="valid-single"),
        pytest.param(
            [
                AnalogInputTest(ANALOG_INPUT_CONFIG),
                DigitalOutputTest(DIGITAL_OUTPUT_CONFIG),
            ],
            None,
            id="valid-multiple",
        ),
        pytest.param(
            [
                AnalogInputTest(
                    GpioDriverConfig(
                        identifier="test",
                        pin=2,
                        direction="input",
                        driver_module=DRIVER_MODULE,
                    )
                )
            ],
            None,
            id="valid-i2c-ping-used",
        ),
        pytest.param(
            [
                AnalogInputTest(ANALOG_INPUT_CONFIG),
                AnalogInputTest(ANALOG_INPUT_CONFIG),
            ],
            ValueError,
            id="duplicate-identifier",
        ),
        pytest.param(
            [
                AnalogInputTest(ANALOG_INPUT_CONFIG),
                AnalogInputTest(
                    ANALOG_INPUT_CONFIG.model_copy(
                        update={"identifier": "new-identifier"}
                    )
                ),
            ],
            ValueError,
            id="duplicate-identifier-gpio-pin",
        ),
        pytest.param(
            [
                AnalogInputTest(
                    I2cDriverConfig(
                        identifier=token_hex(4),
                        driver_module=DRIVER_MODULE,
                        direction="input",
                        address="0x04",
                    )
                ),
                AnalogInputTest(
                    GpioDriverConfig(
                        identifier="test",
                        pin=2,
                        direction="input",
                        driver_module=DRIVER_MODULE,
                    )
                ),
            ],
            ValueError,
            id="i2c-pin-used",
        ),
        pytest.param(
            [
                AnalogInputTest(
                    I2cDriverConfig(
                        identifier=token_hex(4),
                        driver_module=DRIVER_MODULE,
                        direction="input",
                        address="0x04",
                    )
                ),
                AnalogInputTest(
                    I2cDriverConfig(
                        identifier=token_hex(4),
                        driver_module=DRIVER_MODULE,
                        direction="input",
                        address="0x04",
                    )
                ),
            ],
            ValueError,
            id="duplicate-i2c-address",
        ),
    ],
)
def test_validate_device_address_space(
    drivers: list[CarlosDriver], expected_exception: type[Exception] | None
):
    """This method ensures that the validate_device_address_space() works
    as expected."""

    if expected_exception is not None:
        context = pytest.raises(expected_exception)
    else:
        context = nullcontext()

    with context:
        validate_device_address_space(drivers)
