from datetime import UTC, datetime
from typing import Self

from apscheduler import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger
from carlos.edge.interface.device.driver import (
    InputDriver,
    validate_device_address_space,
)
from carlos.edge.interface.device.driver_config import DriverMetadata
from loguru import logger

from carlos.edge.device.config import load_drivers
from carlos.edge.device.storage.blackbox import Blackbox
from carlos.edge.device.storage.connection import get_async_storage_engine

INPUT_SAMPLE_INTERVAL = 2.5 * 60  # 2.5 minutes
"""The time between two consecutive samples of the input devices in seconds."""


class DriverManager:  # pragma: no cover

    def __init__(self):

        self.drivers = {driver.identifier: driver for driver in load_drivers()}
        validate_device_address_space(self.drivers.values())

        self.blackbox = Blackbox(engine=get_async_storage_engine())

    @property
    def driver_metadata(self) -> list[DriverMetadata]:
        """Returns the metadata of the registered drivers."""

        return [
            DriverMetadata(
                identifier=driver.identifier,
                direction=driver.direction,
                driver_module=driver.config.driver_module,
                signals=driver.signals(),
            )
            for driver in self.drivers.values()
        ]

    def setup(self) -> Self:
        """Sets up the I/O peripherals."""
        for driver in self.drivers.values():
            logger.debug(f"Setting up driver {driver}.")
            driver.setup()

        return self

    async def register_tasks(self, scheduler: AsyncScheduler) -> Self:
        """Registers the tasks of the I/O peripherals."""

        for driver in self.drivers.values():
            if isinstance(driver, InputDriver):
                await scheduler.add_schedule(
                    func_or_task_id=self.read_input,
                    kwargs={"driver_identifier": driver.identifier},
                    trigger=IntervalTrigger(seconds=INPUT_SAMPLE_INTERVAL),
                )

        return self

    async def read_input(self, driver_identifier: str):
        """Reads the value of the input driver."""

        logger.debug(f"Reading data from driver {driver_identifier}.")

        read_start = datetime.now(tz=UTC)
        data = await self.drivers[driver_identifier].read_async()
        read_end = datetime.now(tz=UTC)
        # We assume that the actual read time is in the middle of the
        # start and end time.
        read_act = read_start + (read_end - read_start) / 2

        logger.debug(f"Received data from driver {driver_identifier}: {data}")

        await self.blackbox.record(
            driver_identifier=driver_identifier,
            read_timestamp=read_act,
            data=data,
        )
