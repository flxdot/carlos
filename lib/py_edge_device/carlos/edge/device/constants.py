from importlib import metadata
from pathlib import Path

VERSION = metadata.version(__package__)

CONFIG_FILE = Path.cwd() / "device_config"
