import secrets
from uuid import uuid4

from carlos.edge.device.constants import CONFIG_FILE_NAME
from devtools.context_manager import TemporaryWorkingDirectory
from typer.testing import CliRunner

from ..connection import DEVICE_CONNECTION_FILE_NAME
from . import cli

runner = CliRunner()


def test_create_show(tmp_path):
    """This test checks that the `create` and `show` commands work as expected."""

    device_id = uuid4()
    server_url = f"http://server_url-{secrets.token_hex(4)}"

    with TemporaryWorkingDirectory(tmp_path):

        runner.invoke(
            cli,
            ["config", "create"],
            input="\n".join(
                [
                    str(device_id),
                    server_url,
                    "my-domain.eu.auth0.com",
                    "client_id",
                    "client_secret",
                    "audience",
                    "",
                ]
            ),
        )

        assert tmp_path.joinpath(
            CONFIG_FILE_NAME
        ).exists(), "The device configuration file was not created."
        assert tmp_path.joinpath(
            DEVICE_CONNECTION_FILE_NAME
        ).exists(), "The connection settings file was not created."

        result = runner.invoke(cli, ["config", "show"])

        assert (
            str(device_id) in result.stdout
        ), "The device_id was not found in the output."
        assert (
            server_url in result.stdout
        ), "The server_url was not found in the output."
