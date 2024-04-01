from pathlib import Path

import pytest

from carlos.edge.device.config import DeviceConfig, read_config_file, write_config_file


def test_config_file_io(tmp_path: Path):
    """This test ensures that the I/O function of the config module works."""

    cfg_path = tmp_path / "config"

    with pytest.raises(FileNotFoundError):
        read_config_file(cfg_path, DeviceConfig)

    config = DeviceConfig(device_id="test")

    write_config_file(cfg_path, config)

    assert read_config_file(cfg_path, DeviceConfig) == config
