from enum import Enum
from uuid import UUID


class DeviceId(Enum):
    """Define a couple of device IDs that can be used for testing purposes."""

    ONLINE = UUID("1c25f25f-0207-41eb-8ab4-d9fe069031ff")
    """This device is online."""

    OFFLINE = UUID("fe86328a-8d19-47f4-b1c0-d88f6a89e5a4")
    """Used to test devices that are marked as offline."""

    DISCONNECTED = UUID("0874ecc9-1169-4fb0-80d2-e5b0d08754e4")
    """Used to test devices that have never been connected."""

    UNKNOWN = UUID("95c0524f-1919-4b32-8605-fca957d99a1b")
    """A non existing device."""


EXPECTED_DEVICE_COUNT = len(DeviceId) - 1
