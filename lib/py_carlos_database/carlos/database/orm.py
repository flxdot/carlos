__all__ = [
    "ALL_SCHEMA_NAMES",
    "CarlosDeviceDriverOrm",
    "CarlosDeviceOrm",
    "CarlosDeviceSignalOrm",
    "CarlosModelBase",
    "TimeseriesOrm",
]

import inspect
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    BOOLEAN,
    INTEGER,
    REAL,
    SMALLINT,
    TEXT,
    TIMESTAMP,
    VARCHAR,
    ForeignKey,
    ForeignKeyConstraint,
    text,
)
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
        TEXT(), nullable=True, comment="A description of the device for the user."
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


class CarlosDeviceDriverOrm(CarlosModelBase):
    """Contains the metadata for a given driver of a device."""

    __tablename__ = "device_driver"
    __table_args__ = {
        "schema": CarlosDatabaseSchema.CARLOS.value,
        "comment": _clean_doc(__doc__),
    }

    device_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        ForeignKey(CarlosDeviceOrm.device_id, ondelete="CASCADE"),
        primary_key=True,
        comment="The device the driver belongs to.",
    )
    driver_identifier: Mapped[str] = mapped_column(
        VARCHAR(64),
        primary_key=True,
        comment="The unique identifier of the driver in the context of the device.",
    )
    direction: Mapped[str] = mapped_column(
        VARCHAR(32),
        nullable=False,
        comment="The direction of the IO.",
    )
    driver_module: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=False,
        comment="The module that implements the IO driver.",
    )
    display_name: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=False,
        comment="The name of the driver that is displayed in the UI.",
    )
    is_visible_on_dashboard: Mapped[bool] = mapped_column(
        BOOLEAN(),
        nullable=False,
        comment="Whether the driver is visible on the dashboard.",
    )


class CarlosDeviceSignalOrm(CarlosModelBase):
    """Contains the metadata for a given signal of a driver."""

    __tablename__ = "device_signal"
    __table_args__ = (
        ForeignKeyConstraint(
            ["device_id", "driver_identifier"],
            [CarlosDeviceDriverOrm.device_id, CarlosDeviceDriverOrm.driver_identifier],
            ondelete="CASCADE",
        ),
        {
            "schema": CarlosDatabaseSchema.CARLOS.value,
            "comment": _clean_doc(__doc__),
        },
    )

    timeseries_id: Mapped[int] = mapped_column(
        INTEGER(),
        primary_key=True,
        autoincrement=True,
        comment="The unique identifier of the signal.",
    )
    device_id: Mapped[UUID] = mapped_column(
        SQLUUID(as_uuid=True),
        comment="The device the signal belongs to.",
    )
    driver_identifier: Mapped[str] = mapped_column(
        VARCHAR(64),
        comment="The driver the signal belongs to.",
    )
    signal_identifier: Mapped[str] = mapped_column(
        VARCHAR(64),
        comment="The unique identifier of the signal in the context of the driver.",
    )
    display_name: Mapped[str] = mapped_column(
        VARCHAR(255),
        nullable=False,
        comment="The name of the signal that is displayed in the UI.",
    )
    unit_of_measurement: Mapped[int] = mapped_column(
        SMALLINT(),
        nullable=False,
        comment="The unit of measurement of the driver.",
    )
    is_visible_on_dashboard: Mapped[bool] = mapped_column(
        BOOLEAN(),
        nullable=False,
        comment="Whether the signal is visible on the dashboard.",
    )


class TimeseriesOrm(CarlosModelBase):
    """Holds all numeric and boolean timeseries data."""

    __tablename__ = "timeseries"
    __table_args__ = {
        "comment": _clean_doc(__doc__),
        "schema": CarlosDatabaseSchema.CARLOS.value,
    }

    timestamp_utc: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        primary_key=True,
        comment="The timestamp of the data point in UTC.",
    )
    timeseries_id: Mapped[int] = mapped_column(
        INTEGER(),
        ForeignKey(
            CarlosDeviceSignalOrm.timeseries_id,
            ondelete="CASCADE",
        ),
        primary_key=True,
        comment="The unique identifier series.",
    )
    value: Mapped[Optional[float]] = mapped_column(
        REAL(),
        comment="The value of the data point.",
    )
