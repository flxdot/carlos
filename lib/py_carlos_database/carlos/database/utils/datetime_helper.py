__all__ = ["utcnow"]

from datetime import UTC, datetime


def utcnow() -> datetime:
    """Returns the current time at UTC with the UTC timezone attached."""
    return datetime.utcnow().replace(tzinfo=UTC)
