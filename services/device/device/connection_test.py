import random
import secrets
from pathlib import Path
from string import ascii_lowercase, digits
from uuid import uuid4

import pytest
from carlos.edge.device.config import write_config_file
from carlos.edge.interface import DeviceId
from devtools.context_manager import TemporaryWorkingDirectory

from .connection import ConnectionSettings, read_connection_settings


def rand_printable_letters(length: int) -> str:
    return "".join(random.choices(ascii_lowercase + digits, k=length))


class TestConnectionSettings:

    @pytest.fixture(
        scope="class",
        params=[
            "example.com",
            f"{rand_printable_letters(8)}.com",
        ],
    )
    def domain(self, request) -> str:
        """Returns a bunch of domain names."""

        return request.param

    @pytest.fixture(
        scope="class",
    )
    def settings(self, domain: str) -> ConnectionSettings:
        """Returns a bunch of connection settings."""

        return ConnectionSettings(server_url=f"http://{domain}")

    @pytest.fixture()
    def random_device_id(self) -> DeviceId:
        """Returns a random device ID."""

        return uuid4()

    def test_get_websocket_uri(
        self, settings: ConnectionSettings, domain: str, random_device_id: DeviceId
    ):
        """This function ensures that the websocket URI can be read."""

        uri = settings.get_websocket_uri(device_id=random_device_id)

        assert uri.startswith("ws://") or uri.startswith(
            "wss://"
        ), "The URI schema was not correct."
        assert domain in uri, "Domain was not in the URI."
        assert str(random_device_id) in uri, "Device ID was not in the URI."
        assert "token=" not in uri, "URI contained the token although it should not."

        token = secrets.token_urlsafe(16)
        uri_with_token = settings.get_websocket_uri(
            device_id=random_device_id, token=token
        )
        assert uri_with_token.startswith("ws://") or uri_with_token.startswith(
            "wss://"
        ), "The URI schema was not correct."
        assert domain in uri_with_token, "Domain was not in the URI."
        assert str(random_device_id) in uri_with_token, "Device ID was not in the URI."
        assert f"token={token}" in uri_with_token, "URI did not contain the token."

    def test_get_websocket_token_uri(
        self, settings: ConnectionSettings, domain: str, random_device_id: DeviceId
    ):
        """This function ensures that the websocket token URI can be read."""

        uri = settings.get_websocket_token_uri(device_id=random_device_id)

        assert uri.startswith("http://") or uri.startswith(
            "https://"
        ), "The URI schema was not correct."
        assert domain in uri, "Domain was not in the URI."
        assert str(random_device_id) in uri, "Device ID was not in the URI."


def test_read_connection_settings(tmp_path: Path):
    """This function ensures that the connection settings can be read."""

    settings = ConnectionSettings(server_url="http://example.com")

    write_config_file(path=tmp_path / "device_connection", config=settings)

    with TemporaryWorkingDirectory(tmp_path):
        read_settings = read_connection_settings()
        assert read_settings == settings, "The settings where different."
