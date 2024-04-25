__all__ = [
    "TimeseriesIndex",
    "TimeseriesIndexMutation",
    "find_timeseries_index",
    "create_timeseries_index",
    "update_timeseries_index",
    "delete_timeseries_index",
    "get_timeseries_index",
]

from carlos.edge.interface.device.driver_config import DRIVER_IDENTIFIER_LENGTH
from carlos.edge.interface.types import CarlosSchema
from pydantic import Field
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncConnection

from carlos.edge.device.storage.exceptions import NotFoundError
from carlos.edge.device.storage.orm import TimeseriesIndexOrm


class _TimeseriesIndexMixin(CarlosSchema):
    """This class represents the timeseries_index table in the database."""

    driver_identifier: str = Field(
        ...,
        max_length=DRIVER_IDENTIFIER_LENGTH,
        description="Same as the identifier of the driver.",
    )

    driver_signal: str = Field(
        ...,
        max_length=DRIVER_IDENTIFIER_LENGTH,
        description="The signal name of the driver.",
    )

    server_timeseries_id: int | None = Field(
        None,
        description="The unique identifier of timeseries on the carlos server."
        "If this is None then the data is not synced with the server yet.",
    )


class TimeseriesIndex(_TimeseriesIndexMixin):
    """This class represents the timeseries_index table in the database."""

    timeseries_id: int = Field(
        ...,
        description="The unique identifier to be used for the data in the "
        "timeseries_data table.",
    )


class TimeseriesIndexMutation(_TimeseriesIndexMixin):
    """This class represents the timeseries_index table in the database."""


async def find_timeseries_index(
    connection: AsyncConnection,
    driver_identifier: str | None = None,
    driver_signal: str | None = None,
) -> list[TimeseriesIndex]:
    """This function returns the matching timeseries_id for the given driver_identifier
    and driver_signal.

    :param connection: The connection to the database.
    :param driver_identifier: If provided, only the timeseries matching this
        driver_identifier will be returned.
    :param driver_signal: If provided, only the timeseries matching this
        driver_signal will be returned.
    :return: The list of matching timeseries_id.
    """

    query = select(TimeseriesIndexOrm).order_by(TimeseriesIndexOrm.timeseries_id)

    if driver_identifier is not None:
        query = query.where(TimeseriesIndexOrm.driver_identifier == driver_identifier)
    if driver_signal is not None:
        query = query.where(TimeseriesIndexOrm.driver_signal == driver_signal)

    matching = (await connection.execute(query)).all()

    return [TimeseriesIndex.model_validate(match) for match in matching]


async def get_timeseries_index(
    connection: AsyncConnection, timeseries_id: int
) -> TimeseriesIndex:
    """This function returns the timeseries_index table.

    :return: The timeseries_index table.
    :raises NotFoundError: If the timeseries_id is not found.
    """

    query = select(TimeseriesIndexOrm).where(
        TimeseriesIndexOrm.timeseries_id == timeseries_id
    )

    try:
        index = (await connection.execute(query)).one()
    except NoResultFound:
        raise NotFoundError(f"Timeseries with {timeseries_id=} not found")

    return TimeseriesIndex.model_validate(index)


async def create_timeseries_index(
    connection: AsyncConnection, timeseries_index: TimeseriesIndexMutation
) -> TimeseriesIndex:
    """This function creates a new timeseries_index.

    :param connection: The connection to the database.
    :param timeseries_index: The timeseries_index to be created.
    :return: The created timeseries.
    """

    stmt = (
        insert(TimeseriesIndexOrm)
        .values(**timeseries_index.model_dump())
        .returning(TimeseriesIndexOrm)
    )

    created = (await connection.execute(stmt)).one()
    await connection.commit()

    return TimeseriesIndex.model_validate(created)


async def update_timeseries_index(
    connection: AsyncConnection,
    timeseries_id: int,
    server_timeseries_id: int | None = None,
) -> TimeseriesIndex:
    """This function updates the timeseries_index.

    :param connection: The connection to the database.
    :param timeseries_id: The timeseries_id to be updated.
    :param server_timeseries_id: The server_timeseries_id to be updated.
    :return: The updated timeseries.
    :raises NotFoundError: If the timeseries_id is not found.
    """

    stmt = (
        update(TimeseriesIndexOrm)
        .values(server_timeseries_id=server_timeseries_id)
        .where(TimeseriesIndexOrm.timeseries_id == timeseries_id)
        .returning(TimeseriesIndexOrm)
    )

    try:
        updated = (await connection.execute(stmt)).one()
        await connection.commit()
    except NoResultFound:
        raise NotFoundError(f"Timeseries with {timeseries_id=} not found")

    return TimeseriesIndex.model_validate(updated)


async def delete_timeseries_index(
    connection: AsyncConnection, timeseries_id: int
) -> None:
    """This function deletes the timeseries_index.

    :param connection: The connection to the database.
    :param timeseries_id: The timeseries_id to be deleted.
    :raises NotFoundError: If the timeseries_id is not found.
    """

    stmt = delete(TimeseriesIndexOrm).where(
        TimeseriesIndexOrm.timeseries_id == timeseries_id
    )

    await connection.execute(stmt)
    await connection.commit()
