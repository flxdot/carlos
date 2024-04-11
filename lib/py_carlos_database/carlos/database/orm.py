__all__ = ["CarlosModelBase", "ALL_SCHEMA_NAMES"]

import inspect
from enum import Enum

from sqlalchemy.orm import DeclarativeBase


class CarlosSchema(str, Enum):
    """A list of the available schemas in the Carlos database."""

    CARLOS = "carlos"


ALL_SCHEMA_NAMES = sorted([schema.value for schema in CarlosSchema])


def _clean_doc(comment: str) -> str:
    """Clean the comment string to be used in the ORM models.

    :param comment: The comment string to clean.
    :return: The cleaned comment string.
    """
    return inspect.cleandoc(comment).replace("\n", " ")  # pragma: no cover


class CarlosModelBase(DeclarativeBase):
    """Base class for all Qmulus ORM classes."""
