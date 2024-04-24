from importlib import metadata

from carlos.edge.interface.data_directory import DATA_DIRECTORY

VERSION = metadata.version(__package__)

CONFIG_FILE_NAME = "device_config"

LOCAL_DEVICE_STORAGE_PATH = DATA_DIRECTORY / "device"
