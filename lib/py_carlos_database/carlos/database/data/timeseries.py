__all__ = [
    "DatetimeRange",
    "MAX_QUERY_RANGE",
    "TimeseriesData",
    "add_timeseries",
    "get_timeseries",
]
import warnings
from datetime import datetime, timedelta
from typing import Collection, Iterable, Self, Sequence

from more_itertools import batched
from pydantic import Field, field_validator, model_validator
from sqlalchemy import Row, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from carlos.database.context import RequestContext
from carlos.database.error_handling import PostgresErrorCodes, is_postgres_error_code
from carlos.database.exceptions import NotFound
from carlos.database.orm import CarlosDeviceSignalOrm, TimeseriesOrm
from carlos.database.schema import CarlosSchema
from carlos.database.utils import utcnow
from carlos.database.utils.partitions import MonthlyPartition, create_partition
from carlos.database.utils.timestamp_utils import validate_datetime_timezone_utc
from carlos.database.utils.values import prevent_real_overflow


class TimeseriesData(CarlosSchema):
    """Holds the timeseries data of a signale sensor."""

    timeseries_id: int = Field(
        ..., description="The unique identifier of the timeseries."
    )

    timestamps: list[datetime] = Field(
        ...,
        description="The timestamps of the individual samples. "
        "Each timestamp needs to be timezone aware.",
    )

    @field_validator("timestamps")
    def _validate_timestamps_are_tz_aware(cls, value):
        """Ensures that each timestamp is timezone aware."""

        return [validate_datetime_timezone_utc(ts) for ts in value]

    values: list[float | None] = Field(
        ..., description="THe values of the individual samples."
    )

    @model_validator(mode="after")
    def _validate_number_of_samples_equal(self):
        """This validator ensures that the values and timestamp are of equal length."""

        if len(self.values) != len(self.timestamps):
            raise ValueError("Values and timestamps have to be of equal length.")

        return self


class DatetimeRange(CarlosSchema):
    """Defines are range of datetimes. This object can be use for filtering of
    timeseries data."""

    start_at_utc: datetime = Field(
        ..., description="The start of range. Must be timezone aware."
    )

    end_at_utc: datetime = Field(
        ..., description="The end of the range. Must be timezone aware."
    )

    @field_validator("start_at_utc", "end_at_utc")
    def _validate_is_timezone_aware(cls, value):
        """Ensures that the start and end are timezone aware."""

        return validate_datetime_timezone_utc(value)

    @model_validator(mode="after")
    def _validate_order(self) -> Self:
        """Ensures that the start id before the end."""

        if self.start_at_utc > self.end_at_utc:
            raise ValueError("The start can not before the end.")
        if self.start_at_utc == self.end_at_utc:
            raise ValueError("The specified range is empty.")

        return self

    @classmethod
    def from_timedelta(
        cls, td: timedelta, start_at_utc: datetime | None = None
    ) -> Self:
        """Constructs a filter from a timedelta."""

        start_at_utc = start_at_utc or utcnow()
        return cls(
            start_at_utc=start_at_utc,
            end_at_utc=start_at_utc + td,
        )


_TIMESERIES_MAX_BATCH_SIZE = 1000

ValueType = int | float | bool | None


class DuplicateTimestamp(Warning):
    """Issued when duplicate timestamps are found in the data."""


async def add_timeseries(
    context: RequestContext,
    timeseries_id: int,
    timestamps: Sequence[datetime],
    values: Sequence[ValueType],
):
    """Adds timeseries data to the database.

    ⚠️ Warning: Using this function may lead to loss of data if the connection
    contains uncommitted data. This is because the function may need to rollback
    the current transaction in case the underlying partition tables are not existent.
    In that case they will be created but with the cost of loosing any uncommitted
    data.

    :param context: The request context.
    :param timeseries_id: The timeseries_id to add the timeseries data to
    :param timestamps: The timestamps to add
    :param values: The values to add.
        Values are allowed to be of type float, integer, boolean or None. Values will be
        converted to float (except None) before being stored in the database.
    :raises ValueError: If the length of timestamps and values are not equal, the
        provided timeseries_id is not a timeseries, or the timestamps contain timzone
        naive datetime objects.
    :raises EntityNotFound: If the timeseries_id does not exist in the database
    """
    sample_cnt = len(values)
    if len(timestamps) != sample_cnt:
        raise ValueError("The length of timestamps and values must be equal")

    # could be optimized by parallelize the inserts
    # It would still wait for the DB, but python also needs some time to prepare the
    # data
    for batched_zip in batched(zip(timestamps, values), _TIMESERIES_MAX_BATCH_SIZE):
        values_to_insert = _build_values_to_insert(
            timeseries_id=timeseries_id, series=batched_zip
        )

        insert_stmt = insert(TimeseriesOrm)
        insert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=TimeseriesOrm.__table__.primary_key,
            set_={"value": insert_stmt.excluded.value},  # pylint: disable=no-member
        )

        try:
            await context.connection.execute(insert_stmt, values_to_insert)
            await context.connection.commit()
        except IntegrityError as err:
            await context.connection.rollback()
            if is_postgres_error_code(err, PostgresErrorCodes.CHECK_VIOLATION):
                # A check violation error does not necessarily only mean that the
                # partition is missing. But since the timeseries table has not other
                # checks defined we can assume that this is the case.
                await _handle_missing_partitions(
                    context=context, values=values_to_insert  # type: ignore
                )

                await context.connection.execute(insert_stmt, values_to_insert)
                await context.connection.commit()
                continue
            raise  # pragma: no cover


def _build_values_to_insert(
    timeseries_id: int, series: Iterable[tuple[datetime, ValueType]]
) -> list[dict[str, datetime | float | int | None]]:
    """Builds the values to insert into the database.

    It does remove duplicate timestamps and converts the values to floats.
    """

    values_to_insert: dict[datetime, dict[str, datetime | float | int | None]] = {}
    for timestamp, value in series:
        if timestamp in values_to_insert:
            values_to_insert[timestamp]["value"] = _coalesce_values(
                # mypy can not know the type of the value field
                values_to_insert[timestamp]["value"],  # type: ignore
                prevent_real_overflow(value),
            )

            warnings.warn(
                DuplicateTimestamp(
                    f"Found duplicate timestamp for {timeseries_id=} and "
                    f"c{timestamp=}. The values will be coalesced."
                )
            )

            continue

        values_to_insert[timestamp] = {
            "timeseries_id": timeseries_id,
            "timestamp_utc": validate_datetime_timezone_utc(timestamp),
            "value": prevent_real_overflow(value),
        }

    return list(values_to_insert.values())


def _coalesce_values(a: float | None, b: float | None, /) -> float | None:
    """Coalesces two values. Taking the first non None value."""

    return b if a is None else a


async def _handle_missing_partitions(
    context: RequestContext, values: list[dict[str, datetime | float | int]]
):
    """Introspects the values and ensures that the required partitions exist."""

    for partition in _extract_partitions_from_values(values):
        await create_partition(context=context, partition=partition)


def _extract_partitions_from_values(
    values: list[dict[str, datetime | float | int]]
) -> set[MonthlyPartition]:
    """Extracts the years from the timestamps and returns them as a set."""

    return {
        MonthlyPartition.from_timestamp(
            # ignore type because mypy can not know that the value of the key
            # is a datetime
            timestamp=sample["timestamp_utc"],  # type: ignore
            table=TimeseriesOrm,
        )
        for sample in values
    }


MAX_QUERY_RANGE = timedelta(days=30)


async def get_timeseries(
    context: RequestContext,
    timeseries_ids: Collection[int],
    datetime_range: DatetimeRange,
) -> list[TimeseriesData]:
    """Returns a list of TimeseriesData in between the `earliest_date` and
    `latest_date`.

    :param context: request context.
    :param timeseries_ids: List timeseries identifiers to fetch
    :param datetime_range: Defines the timerange in which the timeseries data should
        be fetched
    :raises ValueError: In case timeseries_ids are not provided.
    :raises ValueError: In case that timezone naive datetimes are passed in as
        function arguments
    :raises NotFoundError: In case that any of the requested timeseries_ids does not exist in
        the Timeseries table
    :raises ValueError: If the requested time range exceeds the maximum allowed duration
    :return list[TimeseriesData]: A list of TimeseriesData in ascending order
    """

    if not timeseries_ids:
        raise ValueError(
            "Function argument `timeseries_ids` must not be empty. Please provide "
            "at least one timeseries_id"
        )

    # This check has been introduced to prevent timeouts on the database, in case
    # users/services request too much data at once. This happened in the past
    # as some jobs were marked running for weeks, months or even years.
    if datetime_range.end_at_utc - datetime_range.start_at_utc > MAX_QUERY_RANGE:
        raise ValueError(
            f"Requested time range exceeds the maximum allowed duration of "
            f"{MAX_QUERY_RANGE}. If you need to fetch this amount of data, "
            f"consider splitting the request into smaller chunks."
        )

    # make sure timeseries_ids do not contain duplicates
    timeseries_ids = set(timeseries_ids)

    time_series_query = (
        select(
            TimeseriesOrm.timeseries_id,
            TimeseriesOrm.timestamp_utc,
            TimeseriesOrm.value,
        )
        .where(
            TimeseriesOrm.timeseries_id.in_(timeseries_ids),
            TimeseriesOrm.timestamp_utc >= datetime_range.start_at_utc,
            TimeseriesOrm.timestamp_utc <= datetime_range.end_at_utc,
        )
        .order_by(TimeseriesOrm.timeseries_id.asc(), TimeseriesOrm.timestamp_utc.asc())
    )

    timeseries_result = (await context.connection.execute(time_series_query)).all()

    timeseries_data = _map_timestamp_row_to_timestamp_data(
        result_data=timeseries_result
    )

    # early return if all requested timeseries_ids are available
    if len(timeseries_data) == len(timeseries_ids):
        return timeseries_data

    existing_timeseries_ids = await _get_existing_timeseries_ids(
        context=context, timeseries_ids=timeseries_ids
    )

    missing_timeseries_ids = set(timeseries_ids) - set(existing_timeseries_ids)
    if missing_timeseries_ids:
        raise NotFound(
            f"Requested timeseries_ids {list(missing_timeseries_ids)} are "
            f"not available timeseries."
        )

    # in case that the requested timeseries_ids exist, but did not yield any data
    # we want to return an empty list of x and y values for that timeseries_id
    no_data_timeseries_ids = set(existing_timeseries_ids)
    for time_series in timeseries_data:
        no_data_timeseries_ids.remove(int(time_series.timeseries_id))

    # we need to handle not existing data ids. They could either be missing in the
    # timeseries or be a proxy sensor. For the second case we need to delegate the
    # timeseries_id to a responsible plugin (that create the actual timeseries data)
    for no_data_ts_id in no_data_timeseries_ids:
        ts_data = TimeseriesData(timeseries_id=no_data_ts_id, timestamps=[], values=[])
        timeseries_data.append(ts_data)

    return timeseries_data


async def _get_existing_timeseries_ids(
    context: RequestContext, timeseries_ids: Iterable[int]
) -> list[int]:
    """Returns the subset of existing timeseries_ids from the given timeseries_ids."""

    query = select(CarlosDeviceSignalOrm.timeseries_id).where(
        CarlosDeviceSignalOrm.timeseries_id.in_(timeseries_ids)
    )
    found_ids = (await context.connection.execute(query)).scalars().all()

    return [int(id_) for id_ in found_ids]


def _map_timestamp_row_to_timestamp_data(
    result_data: Sequence[Row] | Sequence[tuple[int, datetime, float]],
) -> list[TimeseriesData]:
    """
    Helper function that maps timestamp_series -> TimeseriesData.

    This function is very opinionated and assumes that the data is sorted by
    timeseries_id and timestamp in ascending order.

    :param result_data: Rows returned from TimeSeries Table
    :return: list of TimeseriesData
    """

    timeseries_data: list[TimeseriesData] = []

    if not result_data:
        return timeseries_data

    timeseries_id = None
    for row in result_data:
        if timeseries_id != row[0]:
            timeseries_data.append(
                TimeseriesData(
                    timeseries_id=row[0], timestamps=[row[1]], values=[row[2]]
                )
            )
            timeseries_id = row[0]

            x_values: list[datetime] = timeseries_data[-1].timestamps
            y_values: list[float | None] = timeseries_data[-1].values

            continue

        # we can ignore F823 here because we can guarantee that
        # the variables are defined above
        # If not, then it should fail loudly
        x_values.append(row[1])  # noqa: F823
        y_values.append(row[2])  # noqa: F823

    return timeseries_data
