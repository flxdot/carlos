__all__ = [
    "ApiTokenOrm",
    "CarlosDeviceModelBase",
    "TimeseriesDataOrm",
    "TimeseriesIndexOrm",
]

from datetime import datetime

from sqlalchemy import DATETIME, FLOAT, INTEGER, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class CarlosDeviceModelBase(DeclarativeBase):
    """Base class for Carlos device models."""


class ApiTokenOrm(CarlosDeviceModelBase):
    __tablename__ = "api_token"

    token: Mapped[str] = mapped_column("token", VARCHAR(4096), primary_key=True)

    valid_until_utc: Mapped[datetime] = mapped_column("valid_until_utc", DATETIME)


class TimeseriesIndexOrm(CarlosDeviceModelBase):
    __tablename__ = "timeseries_index"

    timeseries_id: Mapped[int] = mapped_column(
        "timeseries_id", INTEGER, primary_key=True
    )

    driver_identifier: Mapped[str] = mapped_column(
        "driver_identifier", VARCHAR(64), nullable=False
    )

    driver_signal: Mapped[str] = mapped_column(
        "driver_signal", VARCHAR(64), nullable=False
    )

    server_timeseries_id: Mapped[int | None] = mapped_column(
        "server_timeseries_id", INTEGER, nullable=True
    )


class TimeseriesDataOrm(CarlosDeviceModelBase):
    __tablename__ = "timeseries_data"

    sample_id: Mapped[int] = mapped_column(
        "sample_id", INTEGER, primary_key=True, autoincrement=True
    )

    timeseries_id: Mapped[int] = mapped_column("timeseries_id", INTEGER, nullable=False)

    timestamp_utc: Mapped[int] = mapped_column("timestamp_utc", INTEGER, nullable=False)

    value: Mapped[float] = mapped_column("value", FLOAT, nullable=False)

    staging_id: Mapped[str | None] = mapped_column(
        "staging_id", VARCHAR(4), nullable=True
    )
    staged_at_utc: Mapped[int | None] = mapped_column(
        "staged_at_utc", INTEGER, nullable=True
    )
