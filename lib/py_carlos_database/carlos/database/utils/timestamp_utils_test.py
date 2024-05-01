from contextlib import nullcontext
from datetime import datetime
from math import isclose

import pytest

from .timestamp_utils import interpolate_value_between_dates, validate_timezone


def test_validate_timezone():
    """Test the validate_timezone function."""

    assert validate_timezone("Europe/Berlin") == "Europe/Berlin"

    with pytest.raises(ValueError):
        validate_timezone("Europe/Invalid")


@pytest.mark.parametrize(
    "start_value, end_value, start_datetime, "
    "target_datetime, end_datetime, expected_value, expected_exception",
    [
        pytest.param(
            0,
            1.0,
            datetime(2021, 1, 1, 0, 0, 0),
            datetime(2021, 1, 2, 0, 0, 0),
            datetime(2021, 1, 3, 0, 0, 0),
            0.5,
            None,
            id="Symmetric",
        ),
        pytest.param(
            0,
            99,
            datetime(2021, 1, 1, 0, 0, 0),
            datetime(2021, 1, 9, 0, 0, 0),
            datetime(2021, 1, 10, 0, 0, 0),
            88,
            None,
            id="Asymmetric interpolation",
        ),
        pytest.param(
            10,
            20,
            datetime(2021, 1, 1, 0, 0, 0),
            datetime(2021, 1, 2, 0, 0, 0),
            datetime(2021, 1, 3, 0, 0, 0),
            15,
            None,
            id="With starting offset",
        ),
        pytest.param(
            0,
            1,
            datetime(2021, 1, 2, 0, 0, 0),
            datetime(2021, 1, 1, 0, 0, 0),
            datetime(2021, 1, 3, 0, 0, 0),
            1,
            ValueError,
            id="Target Before range",
        ),
        pytest.param(
            0,
            1,
            datetime(2021, 1, 2, 0, 0, 0),
            datetime(2021, 1, 1, 12, 0, 0),
            datetime(2021, 1, 1, 0, 0, 0),
            1,
            ValueError,
            id="Range incompatible",
        ),
    ],
)
def test_interpolate_value_between_dates(
    start_value: float,
    end_value: float,
    start_datetime: datetime,
    end_datetime: datetime,
    target_datetime: datetime,
    expected_value: float,
    expected_exception: type[Exception] | None,
):
    if expected_exception is None:
        context = nullcontext()
    else:
        context = pytest.raises(expected_exception)

    with context:
        returned_value = interpolate_value_between_dates(
            start_value=start_value,
            end_value=end_value,
            start=start_datetime,
            end=end_datetime,
            target=target_datetime,
        )

        assert isclose(returned_value, expected_value)
