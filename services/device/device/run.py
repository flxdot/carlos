from carlos.edge.device import DeviceRuntime, read_config
from carlos.edge.device.constants import VERSION
from loguru import logger

from device.connection import read_connection_settings
from device.websocket import DeviceWebsocketClient


# can only be tested in integration tests
async def main():  # pragma: no cover
    """The main entry point of the application."""

    logger.info(
        r"""

       ______              __              ____               _           
      / ____/____ _ _____ / /____   _____ / __ \ ___  _   __ (_)_____ ___ 
     / /    / __ `// ___// // __ \ / ___// / / // _ \| | / // // ___// _ \
    / /___ / /_/ // /   / // /_/ /(__  )/ /_/ //  __/| |/ // // /__ /  __/
    \____/ \__,_//_/   /_/ \____//____//_____/ \___/ |___//_/ \___/ \___/ 

        """
    )

    logger.info(f"Starting Carlos device (v{VERSION})...")

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
