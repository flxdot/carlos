import warnings
from datetime import datetime
from typing import Iterable, Sequence

from more_itertools import batched
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from carlos.database.context import RequestContext
from carlos.database.error_handling import PostgresErrorCodes, is_postgres_error_code
from carlos.database.orm import TimeseriesOrm
from carlos.database.utils.partitions import MonthlyPartition, create_partition
from carlos.database.utils.timestamp_utils import validate_datetime_timezone_utc
from carlos.database.utils.values import prevent_real_overflow

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
