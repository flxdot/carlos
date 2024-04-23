__all__ = ["CarlosDeviceModelBase", "ApiTokenOrm"]

from datetime import datetime

from sqlalchemy import DATETIME, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class CarlosDeviceModelBase(DeclarativeBase):
    """Base class for Carlos device models."""


class ApiTokenOrm(CarlosDeviceModelBase):
    __tablename__ = "api_token"

    token: Mapped[str] = mapped_column("token", VARCHAR(4096), primary_key=True)

    valid_until_utc: Mapped[datetime] = mapped_column("valid_until_utc", DATETIME)
