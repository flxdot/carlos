from datetime import datetime, timedelta
from random import randint
from typing import AsyncGenerator

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncConnection

from carlos.edge.device.storage.orm import TimeseriesDataOrm
from carlos.edge.device.storage.timeseries_data import (
    TimeseriesInput,
    add_timeseries_data,
    confirm_staged_data,
    stage_timeseries_data,
)
from carlos.edge.device.storage.timeseries_index import (
    TimeseriesIndex,
    update_timeseries_index,
)


@pytest.fixture()
async def temporary_timeseries_data(
    async_connection: AsyncConnection,
    temporary_timeseries_index: TimeseriesIndex,
) -> AsyncGenerator[list[TimeseriesInput], None]:
    """Creates a temporary timeseries data for testing purposes.

    This fixture also indirectly tests the add_timeseries_data function.
    """

    # ensure that the index has a server_timeseries_id
    await update_timeseries_index(
        connection=async_connection,
        timeseries_id=temporary_timeseries_index.timeseries_id,
        server_timeseries_id=1,
    )

    await async_connection.execute(delete(TimeseriesDataOrm))

    samples_to_insert = randint(10, 300)

    data = []
    start_ts = datetime.utcnow()
    for i in range(samples_to_insert):
        timeseries_input = TimeseriesInput(
            timestamp_utc=start_ts - timedelta(seconds=i),
            values={temporary_timeseries_index.timeseries_id: samples_to_insert - i},
        )
        data.insert(0, timeseries_input)

    for timeseries_input in data:
        await add_timeseries_data(
            connection=async_connection, timeseries_input=timeseries_input
        )

    sample_cnt = (
        await async_connection.execute(func.count(TimeseriesDataOrm.timeseries_id))
    ).scalar()
    if sample_cnt != samples_to_insert:
        pytest.fail(
            f"Failed to insert all samples. Expected {samples_to_insert}, "
            f"got {sample_cnt}."
        )

    yield data

    await async_connection.execute(delete(TimeseriesDataOrm))


async def test_add_timeseries_data(
    async_connection: AsyncConnection,
    temporary_timeseries_data: list[TimeseriesInput],
) -> None:
    """Tests the add_timeseries_data function."""

    rows = (
        await async_connection.execute(
            select(TimeseriesDataOrm).order_by(TimeseriesDataOrm.timestamp_utc)
        )
    ).all()

    temporary_timeseries_data = sorted(
        temporary_timeseries_data, key=lambda x: x.timestamp_utc
    )
    assert len(temporary_timeseries_data) == len(rows)

    for i, timeseries_input in enumerate(temporary_timeseries_data):
        assert rows[i].timestamp_utc == int(timeseries_input.timestamp_utc.timestamp())
        assert rows[i].value == timeseries_input.values[rows[i].timeseries_id]
        assert rows[i].staging_id is None
        assert rows[i].staged_at_utc is None


async def test_staging(
    async_connection: AsyncConnection,
    temporary_timeseries_data: list[TimeseriesInput],
):
    """This test ensures that the staging method works as expected."""

    batch_cnt = randint(2, 5)

    items_to_stage = len(temporary_timeseries_data) // batch_cnt + 1
    assert items_to_stage > 0, "Not enough items to stage."

    # we stage twice to ensure that no data is left that can be staged
    stages = []
    for i in range(batch_cnt):
        staged_items = await stage_timeseries_data(
            connection=async_connection, max_values=items_to_stage
        )
        assert staged_items is not None, "No items were staged."
        assert (
            len(staged_items.data) <= items_to_stage
        ), "Incorrect number of items staged."

        stagged_cnt = (
            await async_connection.execute(
                select(func.count(TimeseriesDataOrm.timeseries_id)).where(
                    TimeseriesDataOrm.staging_id == staged_items.staging_id
                )
            )
        ).scalar()
        assert (
            items_to_stage - batch_cnt <= stagged_cnt <= items_to_stage
        ), "Incorrect number of items staged."

        stages.append(staged_items)

    no_staged_items_left = await stage_timeseries_data(
        connection=async_connection, max_values=items_to_stage
    )
    assert no_staged_items_left is None, "Staged items left in the database."

    for stage in stages:
        await confirm_staged_data(
            connection=async_connection, staging_id=stage.staging_id
        )

        assert (
            await async_connection.execute(
                select(func.count(TimeseriesDataOrm.timeseries_id)).where(
                    TimeseriesDataOrm.staging_id == stage.staging_id
                )
            )
        ).scalar() == 0, "Staged items left in the database."

    # by now all data should have been removed
    assert (
        await async_connection.execute(func.count(TimeseriesDataOrm.timeseries_id))
    ).scalar() == 0, "Data left in the database after staging."
