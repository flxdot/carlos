"""The runtime module contains the device runtime that is used as the main entry point
of the application."""

from carlos.edge.interface import EdgeConnectionDisconnected, EdgeProtocol

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

        communication_handler = DeviceCommunicationHandler(protocol=self.protocol)

        while True:
            if not self.protocol.is_connected:
                await self.protocol.connect()

            try:
                await communication_handler.listen()
            except EdgeConnectionDisconnected:
                await self.protocol.connect()
