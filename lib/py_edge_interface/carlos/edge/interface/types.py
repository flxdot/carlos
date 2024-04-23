__all__ = ["DeviceId", "CarlosSchema"]

from uuid import UUID

from pydantic import BaseModel, ConfigDict

DeviceId = UUID
"""The type of the unique identifier of a device."""


class CarlosSchema(BaseModel):
    """Common base class for all message payloads exchanged between the Carlos backend
    and the Carlos Edge device."""

    model_config = ConfigDict(
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
