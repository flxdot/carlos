from pathlib import Path

from carlos.edge.device.config import read_config_file
from carlos.edge.interface import get_websocket_endpoint, get_websocket_token_endpoint
from pydantic import Field
from pydantic_settings import BaseSettings


class ConnectionSettings(BaseSettings):
    """A selection of settings required to make the connection to the server."""

    server_host: str = Field(..., description="The domain of the server to connect to.")

    use_ssl: bool = Field(True, description="Whether to use SSL for the connection.")

    def get_websocket_uri(self, device_id: str) -> str:
        """Returns the URI of the websocket."""
        return (
            f"ws{'s' if self.use_ssl else ''}://{self.server_host}"
            + get_websocket_endpoint(device_id)
        )

    def get_websocket_token_uri(self, device_id: str) -> str:
        """Returns the URI of the websocket token."""
        return (
            f"http{'s' if self.use_ssl else ''}://{self.server_host}"
            + get_websocket_token_endpoint(device_id)
        )


def read_connection_settings() -> ConnectionSettings:
    """Reads the connection settings from the environment variables."""
    return read_config_file(
        path=Path.cwd() / "device_connection", schema=ConnectionSettings
    )
