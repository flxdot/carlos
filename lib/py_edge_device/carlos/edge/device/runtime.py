"""The runtime module contains the device runtime that is used as the main entry point
of the application."""

import asyncio
import signal
from datetime import timedelta

from apscheduler import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger
from carlos.edge.interface import (
    PING,
    CarlosMessage,
    DeviceConfigPayload,
    DeviceId,
    EdgeProtocol,
    MessageType,
)
from loguru import logger

from .communication import ClientEdgeCommunicationHandler
from .constants import LOCAL_DEVICE_STORAGE_PATH
from .driver_manager import DriverManager
from .storage.migration import alembic_upgrade


# We don't cover this in the unit tests. This needs to be tested in an integration test.
class DeviceRuntime:  # pragma: no cover

    def __init__(self, device_id: DeviceId, protocol: EdgeProtocol):
        """Initializes the device runtime.

        :param device_id: The unique identifier of the device.
        :param protocol: The concrete implementation of the EdgeProtocol.
        """

        self.device_id = device_id

        self.communication_handler = ClientEdgeCommunicationHandler(
            device_id=self.device_id, protocol=protocol
        )
        self.driver_manager = DriverManager()

        self.task_scheduler: AsyncScheduler | None = None

    async def on_connect(self, protocol: EdgeProtocol):
        """This method is called when the protocol connects to the server. It sends the
        device configuration to the server."""

        logger.info("Connected to server.")

        await protocol.send(
            CarlosMessage(
                message_type=MessageType.DEVICE_CONFIG,
                payload=DeviceConfigPayload(
                    drivers=self.driver_manager.driver_metadata
                ),
            )
        )

    async def run(self):
        """Runs the device runtime."""

        self._prepare_runtime()

        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.communication_handler.listen())
            tg.create_task(self._run_task_scheduler())

        logger.debug("Device runtime exited.")

    async def stop(self):
        """Stops the device runtime."""
        self.communication_handler.stop()
        logger.info("Communication handler stopped.")

        await self.task_scheduler.stop()
        logger.info("Task scheduler stopped.")

    async def _handle_signal(self, signum: int):
        """Tries to gracefully stop the device runtime."""

        logger.info(f"Received signal {signum}. Stopping the device runtime.")

        try:
            await asyncio.wait_for(self.stop(), timeout=5)
        except asyncio.TimeoutError:
            logger.error("Stopping the device runtime timed out.")
            exit(1)
        except asyncio.CancelledError:
            pass

        # Give the tasks some time to finish.
        await asyncio.sleep(1)

        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in tasks]
        logger.info(f"Cancelling {len(tasks)} outstanding tasks")
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("Device runtime stopped.")

    def _prepare_runtime(self):
        """Prepares the device runtime."""

        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig, lambda: asyncio.create_task(self._handle_signal(sig))
            )

        # configure the logger
        logger.add(
            sink=LOCAL_DEVICE_STORAGE_PATH / "log" / "device_log_{time}.log",
            level="INFO",
            rotation="50 MB",
            retention=timedelta(days=60),
        )

        # Migrate the local database to the latest version.
        alembic_upgrade()

        # Setup the I/O peripherals.
        self.driver_manager.setup()

    async def _run_task_scheduler(self):
        """Runs the task scheduler."""

        async with AsyncScheduler() as self.task_scheduler:
            logger.debug("Registering tasks.")
            await self.task_scheduler.add_schedule(
                func_or_task_id=send_ping,
                kwargs={"communication_handler": self.communication_handler},
                trigger=IntervalTrigger(minutes=1),
            )
            await self.task_scheduler.add_schedule(
                func_or_task_id=self._send_pending_data,
                trigger=IntervalTrigger(minutes=3),
            )
            await self.driver_manager.register_tasks(scheduler=self.task_scheduler)

            logger.debug("Running task scheduler.")
            await self.task_scheduler.run_until_stopped()

    async def _send_pending_data(self):
        """Sends the pending data to the server."""
        logger.debug("Sending pending data to the server.")
        pass


async def send_ping(
    communication_handler: ClientEdgeCommunicationHandler,
):  # pragma: no cover
    """Sends a ping to the server."""

    if not communication_handler.protocol.is_connected:
        logger.warning("Cannot send ping, as the device is not connected.")
        return

    await communication_handler.send(PING)
