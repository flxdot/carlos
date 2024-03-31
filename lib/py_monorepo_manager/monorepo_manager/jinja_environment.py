from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


def build_environment(template_path: Path) -> Environment:
    """Build a jinja environment from a template path."""

    return Environment(
        loader=FileSystemLoader(template_path),
        autoescape=select_autoescape(),
        keep_trailing_newline=True,
    )
