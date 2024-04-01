from pathlib import Path

from carlos.edge.device.config import read_config_file
from carlos.edge.interface import get_websocket_endpoint, get_websocket_token_endpoint
from carlos.edge.interface.endpoint import append_token_query
from pydantic import Field
from pydantic_settings import BaseSettings


class ConnectionSettings(BaseSettings):
    """A selection of settings required to make the connection to the server."""

    server_host: str = Field(..., description="The domain of the server to connect to.")

    use_ssl: bool = Field(True, description="Whether to use SSL for the connection.")

    def get_websocket_uri(self, device_id: str, token: str | None = None) -> str:
        """Returns the URI of the websocket.

        :param device_id: The ID of the device.
        :param token: The token to use. If the token is passed, it will be added to
        the URI.
        """

        uri_without_token = (
            f"ws{'s' if self.use_ssl else ''}://{self.server_host}"
            + get_websocket_endpoint(device_id)
        )

        if token is None:
            return uri_without_token
        return append_token_query(uri=uri_without_token, token=token)

    def get_websocket_token_uri(self, device_id: str) -> str:
        """Returns the URI of the websocket token.

        :param device_id: The ID of the device.
        """

        return (
            f"http{'s' if self.use_ssl else ''}://{self.server_host}"
            + get_websocket_token_endpoint(device_id)
        )


def read_connection_settings() -> ConnectionSettings:
    """Reads the connection settings from the environment variables."""

    # false positive of mypy
    return read_config_file(  # type: ignore[return-value]
        path=Path.cwd() / "device_connection", schema=ConnectionSettings
    )
