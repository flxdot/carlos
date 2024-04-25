__all__ = [
    "TimeseriesInput",
    "add_timeseries_data",
    "confirm_staged_data",
    "stage_timeseries_data",
]
from datetime import datetime, timedelta

from carlos.edge.interface.messages import DriverDataPayload, DriverTimeseries
from carlos.edge.interface.types import CarlosSchema
from pydantic import Field
from sqlalchemy import delete, insert, or_, select, text, update
from sqlalchemy.ext.asyncio import AsyncConnection

from carlos.edge.device.storage.orm import TimeseriesDataOrm, TimeseriesIndexOrm


class TimeseriesInput(CarlosSchema):

    timestamp_utc: datetime = Field(
        ...,
        description="The timestamp in UTC when the data was recorded.",
    )

    values: dict[int, float] = Field(
        ...,
        description="A mapping of the timeseries_id to the value of "
        "the respective signal.",
    )


async def add_timeseries_data(
    connection: AsyncConnection, timeseries_input: TimeseriesInput
) -> None:
    """Inserts the timeseries data into the database.

    :param connection: The connection to the database.
    :param timeseries_input: The data to be inserted.
    """

    stmt = insert(TimeseriesDataOrm).values(
        [
            {
                "timeseries_id": timeseries_id,
                "timestamp_utc": timeseries_input.timestamp_utc.timestamp(),
                "value": value,
            }
            for timeseries_id, value in timeseries_input.values.items()
        ]
    )

    await connection.execute(stmt)
    await connection.commit()


SQLITE_MAX_VARIABLE_NUMBER = 999
"""The maximum number of variables that can be used in a single query."""


async def stage_timeseries_data(
    connection: AsyncConnection, max_values: int = 250
) -> DriverDataPayload | None:
    """Stages any pending data from the timeseries_data table.

    This function seeks the latest values from the timeseries_data table and stages
    them by setting the staging_id to the payload's staging_id. The data is then
    returned in a DriverDataPayload object.
    """

    if max_values > SQLITE_MAX_VARIABLE_NUMBER:
        raise ValueError(  # pragma: no cover
            f"max_values cannot be greater than {SQLITE_MAX_VARIABLE_NUMBER}."
            "This is a limitation of SQLite."
        )

    payload = DriverDataPayload(data={})

    staging_time = datetime.utcnow()
    expired_staging_time = staging_time - timedelta(minutes=30)

    rowids_query = (
        select(text("rowid"))
        .select_from(TimeseriesDataOrm)
        .where(
            # Only select rows that are
            # - not staged or have an expired staging time
            # - have a server_timeseries_id
            or_(
                TimeseriesDataOrm.staging_id.is_(None),
                TimeseriesDataOrm.timestamp_utc < expired_staging_time.timestamp(),
            ),
            TimeseriesIndexOrm.server_timeseries_id.isnot(None),
        )
        .join(
            TimeseriesIndexOrm,
            TimeseriesIndexOrm.timeseries_id == TimeseriesDataOrm.timeseries_id,
        )
        # we want to stage newest data first
        .order_by(TimeseriesDataOrm.timestamp_utc.desc())
        .limit(max_values)
    )
    rowids = (await connection.execute(rowids_query)).scalars().all()

    stage_stmt = (
        update(TimeseriesDataOrm)
        .values(
            {
                "staging_id": payload.staging_id,
                "staged_at_utc": staging_time.timestamp(),
            }
        )
        .where(text("rowid IN :rowids"))
        .returning(TimeseriesDataOrm)
    )
    staged_rows = (await connection.execute(stage_stmt, {"rowids": rowids})).all()
    await connection.commit()

    if not staged_rows:
        return None

    for row in staged_rows:
        if row.timeseries_id not in payload.data:
            payload.data[row.timeseries_id] = DriverTimeseries(
                timestamps_utc=[], values=[]
            )
        dt = payload.data[row.server_timeseries_id]
        dt.timestamps_utc.append(row.timestamp_utc)
        dt.values.append(row.value)

    return payload


async def confirm_staged_data(connection: AsyncConnection, staging_id: str) -> None:
    """Confirming the staged data means, that the data has been successfully sent to the
    server and can be deleted from the database.

    :param connection: The connection to the database.
    :param staging_id: The staging_id to confirm.
    """

    stmt = delete(TimeseriesDataOrm).where(TimeseriesDataOrm.staging_id == staging_id)

    await connection.execute(stmt)
    await connection.commit()
