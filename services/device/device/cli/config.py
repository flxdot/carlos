from __future__ import print_function, unicode_literals

from typing import TypeVar

import typer
from carlos.edge.device import DeviceConfig
from carlos.edge.device.config import write_config, read_config
from pydantic import BaseModel
from pydantic_core import PydanticUndefinedType
from rich import print_json, print

from device.connection import ConnectionSettings, write_connection_settings, \
    read_connection_settings

config_cli = typer.Typer()


Model = TypeVar("Model", bound=BaseModel)


def ask_pydantic_model(model: type[Model]) -> Model:
    """Asks the user to fill the values of a pydantic model."""

    answers = {}
    for name, field in model.__fields__.items():
        prompt_kwargs = {
            "text": field.description,
            "type": field.annotation,
        }
        if not isinstance(field.default, PydanticUndefinedType):
            prompt_kwargs["default"] = field.default

        answer = typer.prompt(**prompt_kwargs)

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
