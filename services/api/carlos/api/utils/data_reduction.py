__all__ = ["optimize_timeseries"]
from datetime import timedelta

from carlos.database.data.timeseries import TimeseriesData

DEFAULT_SPLIT_THRESHOLD = timedelta(minutes=15)


def optimize_timeseries(
    timeseries: TimeseriesData,
    sample_reduce_threshold: float = 0.01,
    split_threshold: timedelta = DEFAULT_SPLIT_THRESHOLD,
) -> TimeseriesData:
    """This function optimizes time series for the display in the frontend by,
    injecting None values into data gaps larger than the split_threshold.
    It further more allows to remove consecutive samples if the absolute relative
    change to last sample is less than sample_reduce_threshold.
    """

    if len(timeseries.values) < 2:
        return timeseries

    sample_reduce_threshold = abs(sample_reduce_threshold)
    split_threshold = abs(split_threshold)

    # we always need the first value
    ts_len = len(timeseries.values)
    timestamps = [timeseries.timestamps[0]]
    values = [timeseries.values[0]]
    prev_ts = timeseries.timestamps[0]
    last_added_idx = 0
    for idx, (ts, val) in enumerate(
        zip(timeseries.timestamps[1:], timeseries.values[1:])
    ):
        delta = ts - prev_ts
        if delta > split_threshold:
            timestamps.append(prev_ts + delta / 2)
            values.append(None)

        if (
            is_value_changed(
                value=val, previous_value=values[-1], threshold=sample_reduce_threshold
            )
            or idx + 1 == ts_len
        ):
            # if we skipped at least one datapoint, we need to add the right edge
            # of the
            if idx - last_added_idx > 1 and values[-1] is not None:
                # we use idx instead of idx - 1, we would need to use (idx - 1 + 1)
                # due to the loop offset
                timestamps.append(timeseries.timestamps[idx])
                values.append(timeseries.values[idx])
            timestamps.append(ts)
            values.append(val)
            last_added_idx = idx

        prev_ts = ts

    return TimeseriesData(
        timeseries_id=timeseries.timeseries_id, timestamps=timestamps, values=values
    )


def is_value_changed(
    value: float | None, previous_value: float | None, threshold: float
) -> bool:
    """Returns true if the value changed the datatype or the value changed more
    than the threshold (in percent).
    """

    # A 0 threshold means that we need to consider the value always to be changed
    if threshold <= 0.0:
        return True

    # if the data type changed, the value changed for sure
    if not isinstance(value, type(previous_value)):
        return True

    # in case any of the type are none, we just compare the values
    if value is None or previous_value is None:
        return value != previous_value

    if value == previous_value:
        return False

    if value == 0.0 or previous_value == 0.0:
        return True

    return abs(previous_value - value) > threshold * previous_value
