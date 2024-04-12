__all__ = ["CarlosSchema", "DateTimeWithTimeZone"]

from abc import ABC
from datetime import datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CarlosSchema(BaseModel, ABC):
    """A common base class for all Pydantic models used in the Carlos project."""

    model_config = ConfigDict(
        # We expect our REST API to be used by JavaScript clients, which
        # usually prefer camelCase over snake_case.
        alias_generator=to_camel,
        # Whether an aliased field may be populated by its name as given by the model
        # attribute, as well as the alias.
        populate_by_name=True,
        # Whether to build models and look up discriminators of tagged unions using
        # python object attributes.
        from_attributes=True,
        # We always want to strip whitespace from strings, as this is usually
        # a potential source of errors.
        str_strip_whitespace=True,
    )


def _validate_has_timezone(dt: datetime) -> datetime:
    """A custom validator that ensures that the datetime object has a timezone."""

    if dt.tzinfo is None:
        raise ValueError("The datetime object must have a timezone.")
    return dt


DateTimeWithTimeZone = Annotated[datetime, AfterValidator(_validate_has_timezone)]
