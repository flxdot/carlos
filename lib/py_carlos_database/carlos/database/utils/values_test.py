import pytest

from .values import MAX_ABS_REAL_VALUE, prevent_real_overflow, validate_float


@pytest.mark.parametrize(
    "value, expected_value",
    [
        pytest.param(None, None, id="None"),
        pytest.param(1, 1.0, id="integer"),
        pytest.param(False, 0.0, id="boolean"),
        # This value has been encountered in the NPM log files
        pytest.param(
            -1.7976931348623157e308, -MAX_ABS_REAL_VALUE, id="large negative float"
        ),
        pytest.param(
            1.7976931348623157e308, MAX_ABS_REAL_VALUE, id="large positive float"
        ),
        pytest.param(float("nan"), None, id="NaN"),
        pytest.param(float("inf"), None, id="Infinity"),
        pytest.param(float("-inf"), None, id="-Infinity"),
    ],
)
def test_prevent_real_overflow(
    value: int | float | bool | None, expected_value: float | None
):
    """Ensures that the prevent_real_overflow() return the expected values."""

    assert prevent_real_overflow(value) == expected_value


@pytest.mark.parametrize(
    "value, expected_value",
    [
        pytest.param(None, None, id="None"),
        pytest.param(1, 1.0, id="integer"),
        pytest.param(False, 0.0, id="boolean"),
        pytest.param(float("nan"), None, id="NaN"),
        pytest.param(float("inf"), None, id="Infinity"),
        pytest.param(float("-inf"), None, id="-Infinity"),
    ],
)
def test_validate_float(value: float | None, expected_value: float | None):
    """Ensures that the validate_float() return the expected values."""

    assert validate_float(value) == expected_value
