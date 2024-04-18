from __future__ import print_function, unicode_literals

from typing import TypeVar

import typer
from carlos.edge.device.runtime import IoManager
from pydantic import BaseModel
from pydantic_core import PydanticUndefinedType
from rich import print, print_json
from rich.console import Console

from device.connection import (
    ConnectionSettings,
    read_connection_settings,
    write_connection_settings,
)

console = Console()

config_cli = typer.Typer()


Model = TypeVar("Model", bound=BaseModel)


def ask_pydantic_model(model: type[Model]) -> Model:
    """Asks the user to fill the values with a pydantic model."""

    answers = {}
    for name, field in model.model_fields.items():
        prompt_kwargs = {}
        if not isinstance(field.default, PydanticUndefinedType):
            prompt_kwargs["default"] = field.default  # pragma: no cover

        question = (field.description or name).strip().rstrip(".")

        if field.annotation is not None and issubclass(field.annotation, BaseModel):
            print(f"\n[bold]{question}[/bold]:")
            answer = ask_pydantic_model(field.annotation)
        else:
            answer = typer.prompt(text=question, type=field.annotation, **prompt_kwargs)

        answers[name] = answer

    return model(**answers)


@config_cli.command()
def create():
    """Creates a new configuration file."""

    write_connection_settings(ask_pydantic_model(ConnectionSettings))


@config_cli.command()
def show():
    """Prints the current configuration."""

    print("\n[bold]Connection[/bold] configuration:")
    print_json(read_connection_settings().model_dump_json())


@config_cli.command()
def test():  # pragma: no cover
    """Tests the io peripherals."""

    exceptions = {}
    results = {}
    for io in IoManager().setup().ios:
        console.print(f"[cyan]Testing {io} ... [/cyan]", end="")
        try:
            result = io.test()
            console.print("[green]passed[/green]")
            if result:
                results[io.identifier] = result
        except Exception as e:
            console.print("[red]failed[/red]")
            exceptions[io.identifier] = e

    if results:
        console.print("\nThe following IO peripherals returned data:")
        for identifier, result in results.items():
            console.print(f"{identifier}:")
            console.print(result)

    if exceptions:
        console.print("\nThe following IO peripherals [red]failed[/red]:")
        for identifier, exception in exceptions.items():
            console.print(f"[red]{identifier}[/red]:")
            console.print(exception)
