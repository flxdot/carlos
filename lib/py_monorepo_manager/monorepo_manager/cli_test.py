from click.testing import CliRunner

from .cli import cli


def test_cli(own_project_key: str):
    """Ensures the CLI runs without errors."""

    runner = CliRunner()
    result = runner.invoke(cli, ["project", own_project_key])

    assert result.exception is None, "CLI raised an exception"
    assert result.exit_code == 0
