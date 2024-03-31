from carlos.edge.device import DeviceRuntime, read_config

from device.connection import read_connection_settings
from device.websocket import DeviceWebsocketClient, connect


async def main():
    """The main entry point of the application."""
    runtime = DeviceRuntime(
        config=read_config(),
        protocol=DeviceWebsocketClient(
            connection=await connect(settings=read_connection_settings())
        ),
    )
    await runtime.run()


if __name__ == "__main__":

    import asyncio

    asyncio.run(main())
