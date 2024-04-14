from __future__ import print_function, unicode_literals

from typing import TypeVar

import typer
from carlos.edge.device import DeviceConfig
from carlos.edge.device.config import read_config, write_config
from pydantic import BaseModel
from pydantic_core import PydanticUndefinedType
from rich import print, print_json

from device.connection import (
    ConnectionSettings,
    read_connection_settings,
    write_connection_settings,
)

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

        if issubclass(field.annotation, BaseModel):
            print(f"\n[bold]{question}[/bold]:")
            answer = ask_pydantic_model(field.annotation)
        else:
            answer = typer.prompt(text=question, type=field.annotation, **prompt_kwargs)

        answers[name] = answer

    return model(**answers)


@config_cli.command()
def create():
    """Creates a new configuration file."""

    write_config(ask_pydantic_model(DeviceConfig))
    write_connection_settings(ask_pydantic_model(ConnectionSettings))


@config_cli.command()
def show():
    """Prints the current configuration."""
    print("\n[bold]Device[/bold] configuration:")
    print_json(read_config().model_dump_json())

    print("\n[bold]Connection[/bold] configuration:")
    print_json(read_connection_settings().model_dump_json())
