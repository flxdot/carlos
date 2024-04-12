__all__ = [
    "CarlosDevice",
    "CarlosDeviceCreate",
    "CarlosDeviceUpdate",
    "create_device",
    "get_device",
    "list_devices",
    "set_device_seen",
    "update_device",
]

from datetime import timedelta
from uuid import UUID

from pydantic import Field, computed_field
from sqlalchemy import insert, select, update
from sqlalchemy.exc import NoResultFound

from carlos.database.context import RequestContext
from carlos.database.exceptions import NotFound
from carlos.database.orm import CarlosDeviceOrm
from carlos.database.schema import CarlosSchema, DateTimeWithTimeZone
from carlos.database.utils import utcnow

DEVICE_ONLINE_THRESHOLD = timedelta(minutes=5)


class CarlosDeviceCreate(CarlosSchema):
    """Allow you to create a new device."""

    display_name: str = Field(
        ...,
        description="The name of the device that is displayed to the user.",
        max_length=255,
    )
    description: str | None = Field(
        None, description="A description of the device for the user.", max_length=5000
    )


class CarlosDeviceUpdate(CarlosDeviceCreate):
    """Allows you to update the device information."""


class CarlosDevice(CarlosDeviceCreate):
    """Represents an existing device."""

    device_id: UUID = Field(..., description="The unique identifier of the device.")

    registered_at: DateTimeWithTimeZone = Field(
        ..., description="The date and time when the device was registered."
    )
    last_seen_at: DateTimeWithTimeZone | None = Field(
        ..., description="The date and time when the device was last seen."
    )

    @computed_field  # type: ignore
    @property
    def is_online(self) -> bool:
        """Check if the device is online."""
        return (
            self.last_seen_at is not None
            and (utcnow() - self.last_seen_at) < DEVICE_ONLINE_THRESHOLD
        )


async def set_device_seen(
    context: RequestContext,
    device_id: UUID,
) -> None:
    """Updates the last seen timestamp of a device."""

    query = (
        update(CarlosDeviceOrm)
        .where(CarlosDeviceOrm.device_id == device_id)
        .values(last_seen_at=utcnow())
    )
    await context.connection.execute(query)


async def create_device(
    context: RequestContext,
    device: CarlosDeviceCreate,
) -> CarlosDevice:
    """Creates a new device."""

    query = (
        insert(CarlosDeviceOrm)
        .values(
            display_name=device.display_name,
            description=device.description,
            registered_at=utcnow(),
        )
        .returning(CarlosDeviceOrm)
    )
    created = (await context.connection.execute(query)).one()
    return CarlosDevice.model_validate(created)


async def update_device(
    context: RequestContext,
    device_id: UUID,
    device: CarlosDeviceUpdate,
) -> CarlosDevice:
    """Updates the information of a device."""

    query = (
        update(CarlosDeviceOrm)
        .where(CarlosDeviceOrm.device_id == device_id)
        .values(
            display_name=device.display_name,
            description=device.description,
        )
        .returning(CarlosDeviceOrm)
    )

    try:
        updated = (await context.connection.execute(query)).one()
    except NoResultFound:
        raise NotFound(f"No device registered with {device_id=}.")

    return CarlosDevice.model_validate(updated)


async def get_device(
    context: RequestContext,
    device_id: UUID,
) -> CarlosDevice:
    """Retrieves a device by its ID."""

    query = select(CarlosDeviceOrm).where(CarlosDeviceOrm.device_id == device_id)

    try:
        device = (await context.connection.execute(query)).one()
    except NoResultFound:
        raise NotFound(f"No device registered with {device_id=}.")

    return CarlosDevice.model_validate(device)


async def list_devices(
    context: RequestContext,
) -> list[CarlosDevice]:
    """List all devices."""

    query = select(CarlosDeviceOrm)
    devices = (await context.connection.execute(query)).all()
    return [CarlosDevice.model_validate(device) for device in devices]
