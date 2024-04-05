import typer

from .config import config_cli

cli = typer.Typer()
cli.add_typer(config_cli, name="config")


@cli.command()
def run():  # pragma: no cover
    """Runs the device services."""
    import asyncio

    from ..run import main

    asyncio.run(main())


def main():  # pragma: no cover
    """Used to run the CLI."""
    cli()


if __name__ == "__main__":
    cli()
