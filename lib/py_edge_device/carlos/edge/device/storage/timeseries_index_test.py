import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from conftest import TO_CREATE

from .exceptions import NotFoundError
from .timeseries_index import (
    TimeseriesIndex,
    delete_timeseries_index,
    find_timeseries_index,
    get_timeseries_index,
    update_timeseries_index,
)

UNKNOWN_TIMESERIES_ID = 42069


@pytest.mark.parametrize(
    "driver_identifier, driver_signal, expected_result_cnt",
    [
        pytest.param(None, None, 1, id="no_filter"),
        pytest.param(TO_CREATE.driver_identifier, None, 1, id="driver_identifier"),
        pytest.param(None, TO_CREATE.driver_signal, 1, id="driver_signal"),
        pytest.param(
            TO_CREATE.driver_identifier, TO_CREATE.driver_signal, 1, id="both"
        ),
        pytest.param("unknown", None, 0, id="unknown_driver_identifier"),
        pytest.param(None, "unknown", 0, id="unknown_driver_signal"),
        pytest.param("unknown", "unknown", 0, id="unknown_both"),
    ],
)
async def test_find_timeseries_index(
    async_connection: AsyncConnection,
    temporary_timeseries_index: TimeseriesIndex,
    driver_identifier: str | None,
    driver_signal: str | None,
    expected_result_cnt: int,
):
    """Tests the find_timeseries_index function."""

    found = await find_timeseries_index(
        connection=async_connection,
        driver_identifier=driver_identifier,
        driver_signal=driver_signal,
    )

    assert len(found) == expected_result_cnt


async def test_create_timeseries_index(
    async_connection: AsyncConnection, temporary_timeseries_index: TimeseriesIndex
) -> None:
    """Tests the create_timeseries_index function."""

    assert temporary_timeseries_index.driver_identifier == TO_CREATE.driver_identifier
    assert temporary_timeseries_index.driver_signal == TO_CREATE.driver_signal
    assert temporary_timeseries_index.server_timeseries_id is None


async def test_get_timeseries_index(
    async_connection: AsyncConnection, temporary_timeseries_index: TimeseriesIndex
) -> None:
    """Tests the get_timeseries_index function."""

    found = await get_timeseries_index(
        connection=async_connection,
        timeseries_id=temporary_timeseries_index.timeseries_id,
    )

    assert found == temporary_timeseries_index


async def test_get_timeseries_index_not_found(
    async_connection: AsyncConnection, temporary_timeseries_index: TimeseriesIndex
) -> None:
    """Tests the get_timeseries_index function when the timeseries_id is not found."""

    with pytest.raises(NotFoundError):
        await get_timeseries_index(
            connection=async_connection, timeseries_id=UNKNOWN_TIMESERIES_ID
        )


async def test_update_timeseries_index(
    async_connection: AsyncConnection, temporary_timeseries_index: TimeseriesIndex
) -> None:
    """Tests the update_timeseries_index function."""

    new_server_timeseries_id = 42

    updated = await update_timeseries_index(
        connection=async_connection,
        timeseries_id=temporary_timeseries_index.timeseries_id,
        server_timeseries_id=new_server_timeseries_id,
    )
    assert updated.server_timeseries_id == new_server_timeseries_id

    found = await get_timeseries_index(
        connection=async_connection,
        timeseries_id=temporary_timeseries_index.timeseries_id,
    )
    assert found.server_timeseries_id == new_server_timeseries_id


async def test_update_timeseries_index_raise_not_found(
    async_connection: AsyncConnection, temporary_timeseries_index: TimeseriesIndex
) -> None:
    """Tests the update_timeseries_index function when the timeseries_id is
    not found."""

    with pytest.raises(NotFoundError):
        await update_timeseries_index(
            connection=async_connection,
            timeseries_id=UNKNOWN_TIMESERIES_ID,
            server_timeseries_id=42,
        )


async def test_delete_timeseries_index(
    async_connection: AsyncConnection, temporary_timeseries_index: TimeseriesIndex
) -> None:
    """Tests the delete_timeseries_index function."""

    await delete_timeseries_index(
        connection=async_connection,
        timeseries_id=temporary_timeseries_index.timeseries_id,
    )

    # ensure it's gone
    with pytest.raises(NotFoundError):
        await get_timeseries_index(
            connection=async_connection,
            timeseries_id=temporary_timeseries_index.timeseries_id,
        )
