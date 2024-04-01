__all__ = [
    "Context",
    "render_template",
    "write_project_files",
    "write_template",
]
from pathlib import Path
from typing import Any, NamedTuple

from jinja2 import BaseLoader, Environment

from monorepo_manager.language import LanguageProjects
from monorepo_manager.language.python.templates import (
    PYTHON_JINJA_ENVIRONMENT,
    PYTHON_TEMPLATE_TO_PATH,
)
from monorepo_manager.paths import MONOREPO_ROOT
from monorepo_manager.project import Language, Project


class Context(NamedTuple):
    jinja_environment: Environment
    template_to_path: dict[str, str]


LANGUAGE_TO_CONTEXT: dict[Language, Context] = {
    Language.python: Context(
        jinja_environment=PYTHON_JINJA_ENVIRONMENT,
        template_to_path=PYTHON_TEMPLATE_TO_PATH,
    )
}


def write_project_files(project: LanguageProjects | Project):
    """Writes all required project files for the given project."""

    try:
        context = LANGUAGE_TO_CONTEXT[project.language]
    except KeyError:  # pragma: no cover
        # If the project language is not supported, no problem...
        return

    for template, file_path_str in context.template_to_path.items():
        if file_path_str[0] == "/":
            file_path = MONOREPO_ROOT / file_path_str[1:]
        else:
            file_path = project.abs_path / file_path_str

        if "{{" in str(file_path):
            file_path = Path(
                Environment(loader=BaseLoader())
                .from_string(str(file_path))
                .render({"project": project})
            )

        write_template(
            environment=context.jinja_environment,
            file_path=file_path,
            template=template,
            template_kwargs=_build_template_kwargs(
                project=project, file_path=file_path
            ),
        )


def _build_template_kwargs(
    project: LanguageProjects | Project,
    file_path: Path,
) -> dict[str, Any]:
    """Builds the template kwargs for a given project and file path."""
    return {
        "project": project,
        "context": {
            "file_path": file_path,
            "file_name": file_path.name,
            "file_extension": file_path.suffix,
            "file_stem": file_path.stem,
        },
    }


def write_template(
    environment: Environment,
    file_path: Path,
    template: str,
    template_kwargs: dict[str, Any],
):
    """Write a template to a file."""

    file_contents = render_template(
        environment=environment,
        template=template,
        template_kwargs=template_kwargs,
    )

    # The rendering of templates is deactivated by making the template empty.
    if not file_contents.strip():  # pragma: no cover
        return

    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True)  # pragma: no cover

    with open(file_path, "w", encoding="utf-8") as file:
        # ensure that files always contain only one new line at the end
        file.write(file_contents.strip() + "\n")


def write_run_cli_ci(project: LanguageProjects | Project):
    """Internal function to write the invoking script for the CLI."""

    if project.path_from_root.as_posix() != "lib/py_monorepo_manager":
        raise ValueError(
            "This function should only be called for the monorepo manager project."
        )  # pragma: no cover

    file_path = MONOREPO_ROOT / ".github/workflows/monorepo-manager.yml"

    write_template(
        environment=LANGUAGE_TO_CONTEXT[Language.python].jinja_environment,
        file_path=file_path,
        template="run_cli_ci.yml.jinja2",
        template_kwargs=_build_template_kwargs(project=project, file_path=file_path),
    )


def render_template(
    environment: Environment, template: str, template_kwargs: dict[str, Any]
) -> str:
    """Render a template."""

    jinja_template = environment.get_template(name=template)
    return jinja_template.render(**template_kwargs)
