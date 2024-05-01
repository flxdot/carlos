"""This module contains some shared code to ensure that values do not overflow
the database."""

__all__ = [
    "MAX_ABS_REAL_VALUE",
    "prevent_real_overflow",
    "validate_float",
]

import math

# the absolute maximum value that is supported by our DB according to
# https://en.wikipedia.org/wiki/Single-precision_floating-point_format
# Postgres does not really specify this limit
# It will already lead to loss in precision, but we'll still be able to store it
# without error
MAX_ABS_REAL_VALUE = (2 - 2**-23) * 2**127


def prevent_real_overflow(value: int | float | bool | None) -> float | None:
    """This function ensures that values do not exceed the value cap for REAL
    values in Postgres.

    We found glitches where values in the NPM log files have been
    -1.7976931348623157e+308 which can not be stored in Postgres  REAL datatype.
    That's why we need to cap them at the maximum supported size which is
    ~3.4028234663852886e+38.
    """

    # prevents the insert of NaN and Infinity
    value = validate_float(value)

    if value is None:
        return None

    if abs(value) > MAX_ABS_REAL_VALUE:
        return MAX_ABS_REAL_VALUE if value > 0 else -MAX_ABS_REAL_VALUE

    return value


def validate_float(value: float | int | None) -> float | None:
    """This function ensures that special float values such as NaN and Infinity
    are converted to `None` as backend can not serialize them.
    """

    if value is None or math.isnan(value) or math.isinf(value):
        return None
    return float(value)
