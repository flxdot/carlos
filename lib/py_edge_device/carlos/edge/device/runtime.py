"""The runtime module contains the device runtime that is used as the main entry point
of the application."""
from .communication import DeviceCommunicationHandler
from .config import DeviceConfig
from carlos.edge.interface import EdgeProtocol


class DeviceRuntime:

    def __init__(self, config: DeviceConfig, protocol: EdgeProtocol):
        """Initializes the device runtime.

        :param config: The configuration of the device.
        """

        self.config = config
        self.protocol = protocol

    async def run(self):
        """Runs the device runtime."""

        communication_handler = DeviceCommunicationHandler(protocol=self.protocol)
        await communication_handler.listen()
