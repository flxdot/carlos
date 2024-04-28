from datetime import datetime

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine

from .timeseries_data import TimeseriesInput, add_timeseries_data
from .timeseries_index import (
    TimeseriesIndexMutation,
    create_timeseries_index,
    find_timeseries_index,
)


class Blackbox:
    """The black box is used to store measurement data locally on the device. This data
    is stored to be send to the server at a later time. This is useful in case the device
    is not able to send the data to the server immediately. The black box stores the data
    in a SQLite database. The data is stored in the timeseries_data table.
    """

    def __init__(self, engine: AsyncEngine):
        self._engine = engine
        self._timeseries_id_index: dict[str, dict[str, int]] = {}

    async def record(
        self,
        driver_identifier: str,
        read_timestamp: datetime,
        data: dict[str, float],
    ) -> None:
        """Inserts the reading into the database."""

        async with self._engine.connect() as connection:

            await self._ensure_index_hydrated(connection, driver_identifier)

            timeseries_id_to_value: dict[int, float] = {}
            for driver_signal, value in data.items():
                timeseries_id = await self._get_timeseries_id(
                    connection=connection,
                    driver_identifier=driver_identifier,
                    driver_signal=driver_signal,
                )
                timeseries_id_to_value[timeseries_id] = value

            await add_timeseries_data(
                connection=connection,
                timeseries_input=TimeseriesInput(
                    timestamp_utc=read_timestamp, values=timeseries_id_to_value
                ),
            )

            logger.debug(f"Recorded data from driver {driver_identifier}.")

    async def _ensure_index_hydrated(
        self, connection: AsyncConnection, driver_identifier: str
    ):
        """Hydrates the timeseries_id index for the given driver_identifier."""

        if driver_identifier in self._timeseries_id_index:
            return

        matching = await find_timeseries_index(
            connection=connection, driver_identifier=driver_identifier
        )

        driver_index = {}
        for match in matching:
            driver_index[match.driver_signal] = match.timeseries_id
        self._timeseries_id_index[driver_identifier] = driver_index

    async def _get_timeseries_id(
        self, connection: AsyncConnection, driver_identifier: str, driver_signal: str
    ) -> int:
        """Fetches the timeseries_id for the given driver_identifier and driver_signal.
        If the timeseries_id does not exist, it is created and returned.

        :param connection: The connection to the database.
        :param driver_identifier: The driver identifier.
        :param driver_signal: The driver signal.
        :return: The timeseries_id.
        """

        try:
            return self._timeseries_id_index[driver_identifier][driver_signal]
        except KeyError:
            created = await create_timeseries_index(
                connection=connection,
                timeseries_index=TimeseriesIndexMutation(
                    driver_identifier=driver_identifier,
                    driver_signal=driver_signal,
                ),
            )
            self._timeseries_id_index[driver_identifier][
                driver_signal
            ] = created.timeseries_id

            return created.timeseries_id
