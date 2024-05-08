from datetime import UTC, datetime, timedelta

import pytest
from carlos.database.data.timeseries import TimeseriesData

from carlos.api.utils.data_reduction import (
    DEFAULT_SPLIT_THRESHOLD,
    is_value_changed,
    optimize_timeseries,
)


@pytest.mark.parametrize(
    "value, previous_value, threshold, expected",
    [
        pytest.param(None, None, 0.5, False, id="both None"),
        pytest.param(None, 1.0, 0.5, True, id="value None"),
        pytest.param(1.0, None, 0.5, True, id="previous None"),
        pytest.param(1.0, 1.0, 0.0, True, id="no threshold means always changed"),
        pytest.param(1.02, 1.0, 0.01, True, id="value >1% change"),
        pytest.param(1.0, 1.02, 0.01, True, id="previous >1% change"),
        pytest.param(0.02, 0.0, 0.01, True, id="zero - value >1% change"),
        pytest.param(0.0, 0.02, 0.01, True, id="zero - previous >1% change"),
        pytest.param(1.0, 1.0, 0.01, False, id="values equal"),
        pytest.param(0.0, 0.0, 0.01, False, id="zero - value equal"),
        pytest.param(1.009, 1.0, 0.01, False, id="value <1% change"),
        pytest.param(1.0, 1.009, 0.01, False, id="previous <1% change"),
        pytest.param(0.009, 0.0, 0.01, True, id="zero - value true"),
        pytest.param(0.0, 0.009, 0.01, True, id="zero - previous true"),
    ],
)
def test_is_value_changed(
    value: float | None, previous_value: float | None, threshold: float, expected: bool
):
    """This test ensures that we covered all edge cases to detect changes."""

    assert (
        is_value_changed(
            value=value, previous_value=previous_value, threshold=threshold
        )
        is expected
    )


def ts(offset: int) -> datetime:
    """Little helper to reduce the boilerplate to generate test datetimes."""
    return datetime(2024, 1, 1, tzinfo=UTC) + timedelta(seconds=offset)


@pytest.mark.parametrize(
    "ts_in, split_threshold, ts_expected",
    [
        pytest.param(
            TimeseriesData(
                timeseries_id=42,
                timestamps=[],
                values=[],
            ),
            DEFAULT_SPLIT_THRESHOLD,
            TimeseriesData(
                timeseries_id=42,
                timestamps=[],
                values=[],
            ),
            id="empty timeseries",
        ),
        pytest.param(
            TimeseriesData(
                timeseries_id=42,
                timestamps=[ts(0), ts(60), ts(120)],
                values=[1, 1, 2],
            ),
            DEFAULT_SPLIT_THRESHOLD,
            TimeseriesData(
                timeseries_id=42,
                timestamps=[ts(0), ts(120)],
                values=[1, 2],
            ),
            id="duplicate data at beginning",
        ),
        pytest.param(
            TimeseriesData(
                timeseries_id=42,
                timestamps=[ts(i) for i in range(10)],
                values=[1, 2, 2, 2, 2, 2, 2, 3, 3, 4],
            ),
            DEFAULT_SPLIT_THRESHOLD,
            TimeseriesData(
                timeseries_id=42,
                # we want the first and last value of the steady state
                timestamps=[ts(0), ts(1), ts(6), ts(7), ts(8), ts(9)],
                values=[1, 2, 2, 3, 3, 4],
            ),
            id="duplicate in the middle beginning",
        ),
        pytest.param(
            TimeseriesData(
                timeseries_id=42,
                timestamps=[ts(0), ts(120)],
                values=[1, 2],
            ),
            timedelta(seconds=30),
            TimeseriesData(
                timeseries_id=42,
                timestamps=[ts(0), ts(60), ts(120)],
                values=[1, None, 2],
            ),
            id="None inserted in middle of gap",
        ),
    ],
)
def test_optimize_timeseries(
    ts_in: TimeseriesData, ts_expected: TimeseriesData, split_threshold: timedelta
):

    assert optimize_timeseries(ts_in, split_threshold=split_threshold) == ts_expected
