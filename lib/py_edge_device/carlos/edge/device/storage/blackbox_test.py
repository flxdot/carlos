from datetime import UTC, datetime
from random import randint

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncEngine

from .blackbox import Blackbox
from .orm import TimeseriesDataOrm, TimeseriesIndexOrm
from .timeseries_index import find_timeseries_index


async def test_blackbox(async_engine: AsyncEngine):
    """This function ensures that the blackbox works as expected."""

    blackbox = Blackbox(engine=async_engine)

    fake_data = {
        "driver_signal_int": 1,
        "driver_signal_float": 2.0,
        "driver_signal_bool": True,
    }
    driver_identifier = "driver_identifier"

    await blackbox.record(
        driver_identifier=driver_identifier,
        read_timestamp=datetime.now(tz=UTC),
        data=fake_data,
    )

    # check if all index entries are made
    async with async_engine.connect() as connection:
        index_entries = await find_timeseries_index(
            connection, driver_identifier=driver_identifier
        )
        assert len(index_entries) == len(fake_data)

        for index_entry in index_entries:
            assert index_entry.driver_identifier == driver_identifier
            assert index_entry.driver_signal in fake_data
            assert index_entry.server_timeseries_id is None

    sample_cnt = randint(3, 10)

    # Record with multiple blackboxes to hit different paths of the code
    blackbox2 = Blackbox(engine=async_engine)

    # check if the data is recorded correctly
    for _ in range(sample_cnt):
        fake_data = {
            "driver_signal_int": randint(-100, 100),
            "driver_signal_float": randint(-100, 100) * 1.0,
            "driver_signal_bool": bool(randint(0, 1)),
        }

        await blackbox2.record(
            driver_identifier=driver_identifier,
            read_timestamp=datetime.now(tz=UTC),
            data=fake_data,
        )

    # count the number of entries per timeseries_id
    async with async_engine.connect() as connection:
        query = select(
            TimeseriesDataOrm.timeseries_id,
            func.count(TimeseriesDataOrm.timeseries_id).label("sample_cnt"),
        ).group_by(TimeseriesDataOrm.timeseries_id)

        result = (await connection.execute(query)).all()

        for timeseries_id, cnt in result:
            assert cnt == sample_cnt + 1  # +1 because of the first record

    # final cleanup
    async with async_engine.connect() as connection:
        # clean up
        await connection.execute(delete(TimeseriesDataOrm))
        await connection.execute(delete(TimeseriesIndexOrm))
        await connection.commit()
