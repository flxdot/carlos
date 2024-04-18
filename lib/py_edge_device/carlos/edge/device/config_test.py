from pathlib import Path

import pytest
from carlos.edge.interface.device import GpioConfig

from carlos.edge.device.config import read_config_file, write_config_file


def test_config_file_io(tmp_path: Path):
    """This test ensures that the I/O function of the config module works."""

    cfg_path = tmp_path / "config"

    with pytest.raises(FileNotFoundError):
        read_config_file(cfg_path, GpioConfig)

    config = GpioConfig(
        identifier="test-config-file-io",
        ptype="test-config-file-io",
        direction="input",
        pin=7,
    )

    write_config_file(cfg_path, config)

    assert read_config_file(cfg_path, GpioConfig) == config
