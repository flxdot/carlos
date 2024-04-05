from pathlib import Path

from carlos.edge.device.config import read_config_file, write_config_file
from carlos.edge.interface import get_websocket_endpoint, get_websocket_token_endpoint
from carlos.edge.interface.endpoint import append_token_query
from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings


class ConnectionSettings(BaseSettings):
    """A selection of settings required to make the connection to the server."""

    server_url: AnyHttpUrl = Field(
        ...,
        description="Please provide the URL to the Carlos server.",
        examples=["https://carlos.my-domain.com"],
    )

    def get_websocket_uri(self, device_id: str, token: str | None = None) -> str:
        """Returns the URI of the websocket.

        :param device_id: The ID of the device.
        :param token: The token to use. If the token is passed, it will be added to
        the URI.
        """

        uri_without_token = str(self.server_url).replace("http", "ws").strip(
            "/"
        ) + get_websocket_endpoint(device_id)

        if token is None:
            return uri_without_token
        return append_token_query(uri=uri_without_token, token=token)

    def get_websocket_token_uri(self, device_id: str) -> str:
        """Returns the URI of the websocket token.

        :param device_id: The ID of the device.
        """

        return str(self.server_url).strip("/") + get_websocket_token_endpoint(device_id)


DEVICE_CONNECTION_FILE_NAME = "device_connection"


def read_connection_settings() -> ConnectionSettings:
    """Reads the connection settings from the environment variables."""

    return read_config_file(
        path=Path.cwd() / DEVICE_CONNECTION_FILE_NAME, schema=ConnectionSettings
    )


def write_connection_settings(connection_settings: ConnectionSettings):
    """Writes the connection settings to the current working directory."""

    return write_config_file(
        path=Path.cwd() / DEVICE_CONNECTION_FILE_NAME, config=connection_settings
    )
