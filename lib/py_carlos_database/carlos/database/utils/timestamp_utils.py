"""This module contains some reusable functions for working with timestamps."""

__all__ = [
    "convert_to_utc_timezone",
    "interpolate_value_between_dates",
    "validate_datetime_timezone_utc",
    "validate_optional_datetime_timezone_utc",
    "validate_timezone",
]

from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def validate_timezone(timezone: str) -> str:
    """Ensures that the timezone is parsable by the zone-info builtin library.

    :param timezone: The timezone as string to validate.
    :raises ValueError: If the timezone is not valid.
    :return: The timezone as string.
    """

    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError as ex:
        raise ValueError(f"Timezone {timezone} is not valid.") from ex

    return timezone


# A tuple of supported UTC timezones
# Note that we explicitly don't support pytz.UTC timezone.
_UTC_TIMEZONES = (UTC, ZoneInfo("UTC"))


def convert_to_utc_timezone(input_time_with_timezone: datetime) -> datetime:
    """
    Helper function that converts a datetime object to UTC timezone
    if it is not already in UTC timezone.
    :type input_time_with_timezone: object
    """

    return (
        input_time_with_timezone.astimezone(UTC)
        if input_time_with_timezone.tzinfo not in _UTC_TIMEZONES
        else input_time_with_timezone
    )


def validate_datetime_timezone_utc(value: datetime) -> datetime:
    """Ensures that the timezone is set and converts it to UTC."""

    if value.tzinfo is None:
        raise ValueError("Timezone must be set")

    return convert_to_utc_timezone(value)


# excluded from coverage because it is a simple wrapper
def validate_optional_datetime_timezone_utc(  # pragma: no cover
    value: datetime | None,
) -> datetime | None:
    """Ensures that the timezone is set and converts it to UTC."""

    if value is None:
        return None

    return validate_datetime_timezone_utc(value)


def interpolate_value_between_dates(
    start_value: float,
    end_value: float,
    start: datetime,
    end: datetime,
    target: datetime,
) -> float:
    """Interpolates a value between two dates.

    Given a range of datetime and a target datetime to interpolate,
    return the value of the target datetime.

    for example: start _____(left side)_____ target _____(right side)_____ end

    :param start_value: The start value to interpolate.
    :param end_value: The end value to interpolate.
    :param start: The time range to filter the data.
    :param end: The time range to filter the data.
    :param target: The target datetime to interpolate.
    :raises ValueError: If the start datetime is after the end datetime.
    :raises ValueError: If the target datetime is not within the time range.
    :return: The interpolated value.
    """
    if start > end:
        raise ValueError("Start datetime must be before end datetime.")

    if start > target or end < target:
        raise ValueError("The target datetime is not within the time range.")

    total_duration = end - start
    partial_duration = target - start

    return (end_value - start_value) * (partial_duration / total_duration) + start_value
