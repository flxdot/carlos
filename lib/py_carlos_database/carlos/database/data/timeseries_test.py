from datetime import datetime, timedelta
from math import pi, sin

from carlos.database.context import RequestContext
from carlos.database.device import CarlosDeviceSignal
from carlos.database.utils import utcnow

from .timeseries import DatetimeRange, add_timeseries, get_timeseries


async def test_timeseries(
    async_carlos_db_context: RequestContext, driver_signals: list[CarlosDeviceSignal]
):

    span = timedelta(hours=2)
    now = utcnow()
    datetime_range = DatetimeRange(start_at_utc=now - span, end_at_utc=now)

    # read empty data
    empty_ts = await get_timeseries(
        context=async_carlos_db_context,
        timeseries_ids=[signal.timeseries_id for signal in driver_signals],
        datetime_range=datetime_range,
    )
    assert len(empty_ts) == len(driver_signals)
    for ts in empty_ts:
        assert len(ts.values) == 0, "Empty timeseries should have no values"
        assert len(ts.timestamps) == 0, "Empty timeseries should have no timestamps"

    # insert first signal
    n_samples = 500
    data = random_data(datetime_range=datetime_range, n_samples=n_samples)
    await add_timeseries(
        context=async_carlos_db_context,
        timeseries_id=driver_signals[0].timeseries_id,
        timestamps=data[0],
        values=data[1],
    )

    # read first signal
    ts = await get_timeseries(
        context=async_carlos_db_context,
        timeseries_ids=[driver_signals[0].timeseries_id],
        datetime_range=datetime_range,
    )
    assert len(ts) == 1
    assert (
        len(ts[0].values) == n_samples
    ), f"First Timeseries should have {n_samples} values"
    assert (
        len(ts[0].timestamps) == n_samples
    ), f"First Timeseries should have {n_samples} timestamps"

    # reading both signals should still work
    ts = await get_timeseries(
        context=async_carlos_db_context,
        timeseries_ids=[signal.timeseries_id for signal in driver_signals],
        datetime_range=datetime_range,
    )
    assert len(ts) == 2
    for t in ts:
        if t.timeseries_id == driver_signals[0].timeseries_id:
            assert len(t.timestamps) == n_samples
            assert len(t.values) == n_samples
        else:
            assert len(t.timestamps) == 0
            assert len(t.values) == 0

    # insert second signal
    n_samples = 300
    data = random_data(datetime_range=datetime_range, n_samples=n_samples)
    await add_timeseries(
        context=async_carlos_db_context,
        timeseries_id=driver_signals[1].timeseries_id,
        timestamps=data[0],
        values=data[1],
    )

    # read second signal
    ts = await get_timeseries(
        context=async_carlos_db_context,
        timeseries_ids=[driver_signals[1].timeseries_id],
        datetime_range=datetime_range,
    )
    assert len(ts) == 1
    assert (
        len(ts[0].values) == n_samples
    ), f"Second Timeseries should have {n_samples} values"
    assert (
        len(ts[0].timestamps) == n_samples
    ), f"Second Timeseries should have {n_samples} timestamps"

    # read both signals
    ts = await get_timeseries(
        context=async_carlos_db_context,
        timeseries_ids=[signal.timeseries_id for signal in driver_signals],
        datetime_range=datetime_range,
    )
    assert len(ts) == 2


def random_data(datetime_range, n_samples: int) -> tuple[list[datetime], list[float]]:
    """Generates a full sin wave over the given datetime range with
    n_samples samples."""

    delta = (datetime_range.end_at_utc - datetime_range.start_at_utc) / n_samples
    timestamps = [datetime_range.start_at_utc + i * delta for i in range(n_samples)]
    values = [sin(2 * pi * 1 / n_samples) for i in range(n_samples)]

    return timestamps, values
