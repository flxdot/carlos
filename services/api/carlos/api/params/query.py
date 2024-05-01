from datetime import datetime

from carlos.database.data.timeseries import DatetimeRange
from fastapi import Query


def datetime_range(
    start_at_utc: datetime = Query(
        ...,
        alias="startAtUtc",
        description="The start of range. Must be timezone aware.",
    ),
    end_at_utc: datetime = Query(
        ...,
        alias="endAtUtc",
        description="The end of the range. Must be timezone aware.",
    ),
) -> DatetimeRange:
    """Dependency to get the datetime range from the query parameters."""

    return DatetimeRange(start_at_utc=start_at_utc, end_at_utc=end_at_utc)
