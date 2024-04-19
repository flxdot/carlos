from __future__ import print_function, unicode_literals

from typing import TypeVar

import typer
from carlos.edge.device.runtime import DriverManager
from pydantic import BaseModel
from pydantic_core import PydanticUndefinedType
from rich import print, print_json
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.pretty import Pretty
from rich.rule import Rule
from rich.spinner import Spinner
from rich.traceback import Traceback

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

    driver_result_ui = []
    failed = []
    passed_cnt = 0
    with Live(Group(), refresh_per_second=4) as live:
        for driver in DriverManager().setup().drivers:
            driver_result_ui.append(
                Panel(
                    Spinner(name="aesthetic", text="testing..."),
                    padding=(1, 2),
                    title=str(driver),
                    title_align="left",
                    subtitle="testing",
                    subtitle_align="right",
                )
            )
            live.update(Group(*driver_result_ui))

            try:
                result = driver.test()
                driver_result_ui[-1].renderable = Pretty(
                    result or "[green]passed[/green]"
                )
                driver_result_ui[-1].subtitle = "[green]passed[/green]"
                passed_cnt += 1
            except Exception as e:
                failed.append(driver)
                driver_result_ui[-1].renderable = Traceback.from_exception(
                    type(e), e, e.__traceback__
                )
                driver_result_ui[-1].subtitle = "[red]failed[/red]"

        conclusions = []
        if passed_cnt > 0:
            conclusions.append(f"[green]{passed_cnt} passed[/green]")
        if failed:
            conclusions.append(f"[red]{len(failed)} failed[/red]")

        live.update(Group(*driver_result_ui, Rule(", ".join(conclusions))))
