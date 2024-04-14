"""The runtime module contains the device runtime that is used as the main entry point
of the application."""

from apscheduler import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger
from carlos.edge.interface import EdgeConnectionDisconnected, EdgeProtocol
from carlos.edge.interface.protocol import PING

from .communication import DeviceCommunicationHandler
from .config import DeviceConfig


# We don't cover this in the unit tests. This needs to be tested in an integration test.
class DeviceRuntime:  # pragma: no cover

    def __init__(self, config: DeviceConfig, protocol: EdgeProtocol):
        """Initializes the device runtime.

        :param config: The configuration of the device.
        """

        self.config = config
        self.protocol = protocol

    async def run(self):
        """Runs the device runtime."""

        communication_handler = DeviceCommunicationHandler(
            protocol=self.protocol, device_id=self.config.device_id
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


async def send_ping(communication_handler: DeviceCommunicationHandler):
    """Sends a ping to the server."""
    await communication_handler.send(PING)
