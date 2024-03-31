"""Contains functions to load projects from the repository."""

__all__ = ["explore_repo", "project_from_path"]

from pathlib import Path

from monorepo_manager.language.javascript import JavascriptProject
from monorepo_manager.language.python import PythonProject
from monorepo_manager.language.rust import RustProject
from monorepo_manager.paths import LIBRARIES_PATH, SERVICES_PATH

from .project import Language, Project, guess_language


def project_from_path(project_path: Path) -> Project:
    """Create a project from a path."""

    language = guess_language(project_path)

    if language == Language.python:
        return PythonProject.from_path(project_path)
    if language == Language.javascript:  # pragma: no cover
        return JavascriptProject.from_path(project_path)
    if language == Language.rust:  # pragma: no cover
        return RustProject.from_path(project_path)
    if language == Language.binary:  # pragma: no cover
        return Project.from_path(project_path)
    raise ValueError(f"Unknown language: {language}")  # pragma: no cover


def explore_repo() -> list[Project]:
    """Explore the repository and return a list of projects."""

    projects: list[Project] = []

    for library in LIBRARIES_PATH.iterdir():
        if not library.is_dir():
            continue
        projects.append(project_from_path(library))

    for service in SERVICES_PATH.iterdir():
        if not service.is_dir():
            continue  # pragma: no cover
        projects.append(project_from_path(service))

    return sorted(projects, key=lambda project: project.path_from_root)
