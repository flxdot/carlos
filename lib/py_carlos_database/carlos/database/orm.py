__all__ = [
    "ALL_SCHEMA_NAMES",
    "CarlosDeviceOrm",
    "CarlosModelBase",
]

import inspect
from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import TEXT, TIMESTAMP, VARCHAR, text
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class CarlosDatabaseSchema(str, Enum):
    """A list of the available schemas in the Carlos database."""

    CARLOS = "carlos"


ALL_SCHEMA_NAMES = sorted([schema.value for schema in CarlosDatabaseSchema])


def _clean_doc(comment: str) -> str:
    """Clean the comment string to be used in the ORM models.

    :param comment: The comment string to clean.
    :return: The cleaned comment string.
    """
    return inspect.cleandoc(comment).replace("\n", " ")


class CarlosModelBase(DeclarativeBase):
    """Base class for all Carlos ORM classes."""


class CarlosDeviceOrm(CarlosModelBase):
    """Contains all known devices for the tenant."""

    __tablename__ = "device"
    __table_args__ = {
        "schema": CarlosDatabaseSchema.CARLOS.value,
        "comment": _clean_doc(__doc__),
    }

    device_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="The unique identifier of the device.",
    )
    display_name: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=False,
        comment="The name of the device that is displayed to the user.",
    )
    description: Mapped[str] = mapped_column(
        TEXT, nullable=True, comment="A description of the device for the user."
    )
    registered_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("(now() AT TIME ZONE 'UTC'::text)"),
        comment="The date and time when the device was registered.",
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        comment="The date and time when the server last received data from the device.",
    )
