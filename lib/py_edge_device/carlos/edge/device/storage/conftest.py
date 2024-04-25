from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from .timeseries_index import (
    TimeseriesIndex,
    TimeseriesIndexMutation,
    create_timeseries_index,
    delete_timeseries_index,
)

TO_CREATE = TimeseriesIndexMutation(
    driver_identifier="test_driver",
    driver_signal="test_signal",
)


@pytest.fixture()
async def temporary_timeseries_index(
    async_connection: AsyncConnection,
) -> AsyncGenerator[TimeseriesIndex, None]:
    """Creates a temporary timeseries index for testing purposes."""

    created = await create_timeseries_index(
        connection=async_connection, timeseries_index=TO_CREATE
    )

    yield created

    await delete_timeseries_index(
        connection=async_connection, timeseries_id=created.timeseries_id
    )
