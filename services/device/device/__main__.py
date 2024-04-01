from carlos.edge.device import DeviceRuntime, read_config

from device.connection import read_connection_settings
from device.websocket import DeviceWebsocketClient


async def main():
    """The main entry point of the application."""

    device_config = read_config()
    device_connection = read_connection_settings()
    protocol = DeviceWebsocketClient(
        settings=device_connection, device_id=device_config.device_id
    )

    runtime = DeviceRuntime(
        config=device_config,
        protocol=protocol,
    )
    await runtime.run()


if __name__ == "__main__":

    import asyncio

    asyncio.run(main())
