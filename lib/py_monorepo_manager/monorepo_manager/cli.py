"""This module contains the command line interface for the monorepo."""
import json

import click
import yaml

from monorepo_manager.graph import depth_first_search
from monorepo_manager.language import (
    JavascriptProject,
    LanguageProjects,
    PythonProject,
    RustProject,
)
from monorepo_manager.loading import explore_repo
from monorepo_manager.paths import METADATA_PATH, QMULUS_REPO_PATH
from monorepo_manager.project import Language, Project
from monorepo_manager.template_renderer import (
    Context,
    write_project_files,
    write_run_cli_ci,
    write_template,
)
from monorepo_manager.templates import (
    GENERAL_JINJA_ENVIRONMENT,
    GENERAL_TEMPLATE_TO_PATH,
)

ProjectUnion = LanguageProjects | Project


def parse_project(project_data: dict[str, dict]) -> ProjectUnion:
    """Parse a project from a dictionary."""

    if "language" in project_data:
        try:
            language = Language(project_data["language"])
        except ValueError:  # pragma: no cover
            return Project.model_validate(project_data)

        if language == Language.python:
            return PythonProject.model_validate(project_data)
        if language == Language.javascript:
            return JavascriptProject.model_validate(project_data)
        if language == Language.rust:
            return RustProject.model_validate(project_data)
        return Project.model_validate(project_data)

    raise ValueError("Invalid project data")  # pragma: no cover


class ProjectsIndex(dict[str, ProjectUnion]):
    """A dictionary of projects."""

    @classmethod
    def from_projects(cls, projects: list[ProjectUnion]) -> "ProjectsIndex":
        """Create a projects index from a list of projects."""
        return cls({str(project.path_from_root): project for project in projects})

    def to_serializable(self) -> dict[str, dict]:
        """Returns a serializable dict of the projects index."""

        return {
            key: json.loads(value.model_dump_json(exclude_unset=True))
            for key, value in self.items()
        }

    @classmethod
    def from_serializable(cls, serializable: dict[str, dict]) -> "ProjectsIndex":
        """Builds a ProjectsIndex from a serializable dict."""

        project_index = cls()
        for key, value in serializable.items():
            try:
                project_index[key] = parse_project(value)
            except FileNotFoundError:  # pragma: no cover
                # this happens when a project is deleted
                pass

        return cls(project_index)

    @property
    def python_projects(self) -> list[str]:
        """Returns a list of all python projects in order of dependency."""

        project_graph = {
            str(project.path_from_root): project.monorepo_dependencies
            for project in self.values()
            if isinstance(project, PythonProject)
        }

        return depth_first_search(graph=project_graph)


def load_metadata() -> ProjectsIndex:
    """Load the metadata of the monorepo."""

    with open(METADATA_PATH, "r", encoding="utf-8") as metadata_file:
        meta_data = yaml.safe_load(metadata_file.read())

    # inject the path from the index
    # this is required because we excluded it from the JSON
    # to reduce redundancy and noise
    for path, project_data in meta_data.items():
        project_data["path_from_root"] = path

    return ProjectsIndex.from_serializable(meta_data)


def write_metadata(projects_index: ProjectsIndex):
    """Write the metadata of the monorepo."""

    with open(METADATA_PATH, "w", encoding="utf-8") as metadata_file:
        # we want to store the file as YAML,
        serialized = yaml.safe_dump(projects_index.to_serializable())
        metadata_file.write(serialized)


def inspect_repo() -> ProjectsIndex:
    """Inspect the repository and return a list of projects.

    This function will manage the state of the metadata file.
    """

    try:
        known_projects = load_metadata()
    except FileNotFoundError:  # pragma: no cover
        known_projects = ProjectsIndex()

    actual_projects = explore_repo()

    project_index = ProjectsIndex.from_projects(actual_projects)

    new_projects = set(project_index.keys()) - set(known_projects.keys())
    for new_project in new_projects:  # pragma: no cover
        known_projects[new_project] = project_index[new_project]
        proj = project_index[new_project]
        print(
            f"New project {proj.__class__.__name__} at {proj.path_from_root} detected."
        )

    write_metadata(known_projects)

    return known_projects


def write_general_files(project_index: ProjectsIndex):
    """Write the general files for the monorepo."""

    context = Context(
        jinja_environment=GENERAL_JINJA_ENVIRONMENT,
        template_to_path=GENERAL_TEMPLATE_TO_PATH,
    )

    for template, file_path in context.template_to_path.items():
        if file_path[0] == "/":
            file_path = file_path[1:]

        write_template(
            environment=context.jinja_environment,
            file_path=QMULUS_REPO_PATH / file_path,
            template=template,
            template_kwargs={"project_index": project_index},
        )


@click.group()
def cli():
    pass


@click.command("all")
def cli_command_all():  # pragma: no cover
    """Run the manager for all projects."""
    proj_index = inspect_repo()
    for project_ in proj_index.values():
        write_project_files(project_)
    write_general_files(proj_index)
    write_run_cli_ci(proj_index["lib/py_monorepo_manager"])


@click.command("project")
@click.argument("project", type=click.STRING)
def cli_command_project(project: str):
    """Run the manager for a specific project."""
    proj_index = inspect_repo()
    write_project_files(proj_index[project])
    write_general_files(proj_index)
    write_run_cli_ci(proj_index["lib/py_monorepo_manager"])


cli.add_command(cli_command_all)
cli.add_command(cli_command_project)

if __name__ == "__main__":  # pragma: no cover
    cli()
