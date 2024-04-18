from pathlib import Path

import pytest
from carlos.edge.interface.device import AnalogInput, DigitalOutput, GpioConfig

from carlos.edge.device.config import load_io, read_config_file, write_config_file
from tests.test_data import EXPECTED_IO_COUNT, TEST_DEVICE_WORKDIR


def test_config_file_io(tmp_path: Path):
    """This test ensures that the I/O function of the config module works."""

    cfg_path = tmp_path / "config"

    with pytest.raises(FileNotFoundError):
        read_config_file(cfg_path, GpioConfig)

    config = GpioConfig(
        identifier="test-config-file-io",
        module="carlos.edge.device.io.dht11",
        direction="input",
        pin=7,
    )

    write_config_file(cfg_path, config)

    assert read_config_file(cfg_path, GpioConfig) == config


def test_load_io():
    """This test ensures that the IOs are loaded correctly."""

    io = load_io(config_dir=TEST_DEVICE_WORKDIR)

    assert len(io) == EXPECTED_IO_COUNT, "The number of IOs does not match."

    assert all(
        isinstance(io, (AnalogInput, DigitalOutput)) for io in io
    ), "Not all IOs are of the correct type."
