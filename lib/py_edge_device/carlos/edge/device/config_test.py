from pathlib import Path
from uuid import uuid4

import pytest

from carlos.edge.device.config import read_config_file, write_config_file
from carlos.edge.interface.device import DeviceConfig


def test_config_file_io(tmp_path: Path):
    """This test ensures that the I/O function of the config module works."""

    cfg_path = tmp_path / "config"

    with pytest.raises(FileNotFoundError):
        read_config_file(cfg_path, DeviceConfig)

    config = DeviceConfig(device_id=uuid4())

    write_config_file(cfg_path, config)

    assert read_config_file(cfg_path, DeviceConfig) == config
