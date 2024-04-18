"""The runtime module contains the device runtime that is used as the main entry point
of the application."""

from datetime import timedelta
from pathlib import Path

from apscheduler import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger
from carlos.edge.interface import DeviceId, EdgeConnectionDisconnected, EdgeProtocol
from carlos.edge.interface.device.io import validate_device_address_space
from carlos.edge.interface.protocol import PING
from loguru import logger

from .communication import DeviceCommunicationHandler
from .config import load_io


# We don't cover this in the unit tests. This needs to be tested in an integration test.
class DeviceRuntime:  # pragma: no cover

    def __init__(self, device_id: DeviceId, protocol: EdgeProtocol):
        """Initializes the device runtime.

        :param device_id: The unique identifier of the device.
        :param protocol: The concrete implementation of the EdgeProtocol.
        """

        self.device_id = device_id
        self.protocol = protocol

    async def run(self):
        """Runs the device runtime."""

        self._prepare_runtime()

        communication_handler = DeviceCommunicationHandler(
            protocol=self.protocol, device_id=self.device_id
        )

        if not self.protocol.is_connected:
            await self.protocol.connect()

        async with AsyncScheduler() as scheduler:
            await scheduler.add_schedule(
                func_or_task_id=send_ping,
                kwargs={"communication_handler": communication_handler},
                trigger=IntervalTrigger(minutes=1),
            )
            await scheduler.start_in_background()

            while True:
                if not self.protocol.is_connected:
                    await self.protocol.connect()

                try:
                    await communication_handler.listen()
                except EdgeConnectionDisconnected:
                    await self.protocol.connect()

    def _prepare_runtime(self):

        logger.add(
            sink=Path.cwd() / ".carlos_data" / "device" / "device_log_{time}.log",
            level="INFO",
            rotation="50 MB",
            retention=timedelta(days=60),
        )


class IoManager:  # pragma: no cover

    def __init__(self):

        self.ios = load_io()
        validate_device_address_space(self.ios)

    def setup(self):
        """Sets up the I/O peripherals."""
        for io in self.ios:
            logger.debug(
                f"Setting up I/O peripheral {io.config.identifier} ({io.config.module})."
            )
            io.setup()

    def test(self):
        """Tests the I/O peripherals."""
        for io in self.ios:
            logger.debug(
                f"Testing I/O peripheral {io.config.identifier} ({io.config.module})."
            )
            io.test()


async def send_ping(
    communication_handler: DeviceCommunicationHandler,
):  # pragma: no cover
    """Sends a ping to the server."""
    await communication_handler.send(PING)
