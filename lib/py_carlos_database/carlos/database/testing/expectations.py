from enum import Enum
from uuid import UUID


class DeviceId(Enum):
    """Define a couple of device IDs that can be used for testing purposes."""

    ONLINE = UUID("11111111-1111-1111-1111-111111111111")
    """This device is online."""

    OFFLINE = UUID("22222222-2222-2222-2222-222222222222")
    """Used to test devices that are marked as offline."""

    DISCONNECTED = UUID("33333333-3333-3333-3333-333333333333")
    """Used to test devices that have never been connected."""

    DEVICE_A = UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')
    """Used to test interaction with a device."""

    UNKNOWN = UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")
    """A non existing device."""


EXPECTED_DEVICE_COUNT = len(DeviceId) - 1
