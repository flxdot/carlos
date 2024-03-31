from pathlib import Path

from carlos.edge.device.config import read_config_file
from pydantic import Field
from pydantic_settings import BaseSettings


class ConnectionSettings(BaseSettings):
    """A selection of settings required to make the connection to the server."""

    server_host: str = Field(..., description="The domain of the server to connect to.")

    use_ssl: bool = Field(True, description="Whether to use SSL for the connection.")

    @property
    def websocket_uri(self) -> str:
        """Returns the URI of the websocket."""
        return f"ws{'s' if self.use_ssl else ''}://{self.server_host}/edge/server"


def read_connection_settings() -> ConnectionSettings:
    """Reads the connection settings from the environment variables."""
    return read_config_file(
        path=Path.cwd() / "device_connection", schema=ConnectionSettings
    )
