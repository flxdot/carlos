"""This module contains the logic to handle each project in the monorepo."""

__all__ = ["Language", "Project", "guess_language"]

from enum import Enum
from inspect import getdoc
from pathlib import Path

from pydantic import BaseModel, Field

from monorepo_manager.paths import LIBRARIES_PATH, MONOREPO_ROOT


class Language(str, Enum):
    """A programming language."""

    javascript = "javascript"
    python = "python"
    rust = "rust"
    # special case for binary services
    binary = "binary"


class ContinuousIntegration(BaseModel):
    """Defines the settings for the continuous integration."""

    enabled: bool = Field(
        True, description="Whether the continuous integration is enabled."
    )

    additional_files_to_watch: list[str] = Field(
        default_factory=list, description="Additional files to watch for changes."
    )


class Project(BaseModel):
    """A project in the monorepo."""

    path_from_root: Path = Field(
        ...,
        description="The path to the project from the root of the monorepo.",
        exclude=True,  # exclude from JSON, as it's redundant
    )

    language: Language = Field(
        ..., description="The programming language of the project."
    )

    continuous_integration: ContinuousIntegration = Field(
        default_factory=ContinuousIntegration,  # type: ignore
        description=getdoc(ContinuousIntegration),
    )

    @property
    def abs_path(self) -> Path:
        """The absolute path to the project."""

        return MONOREPO_ROOT / self.path_from_root

    @property
    def is_library(self) -> bool:
        """Whether the project is a library."""

        return self.abs_path.parent == LIBRARIES_PATH

    @property
    def is_service(self) -> bool:
        """Whether the project is a service."""

        return not self.is_library

    @property
    def folder(self) -> str:
        """Returns the folder name in the service or lib folder."""

        return self.abs_path.name

    @classmethod
    def from_path(cls, project_path: Path) -> "Project":
        """Create a project from a path."""

        return cls(
            path_from_root=project_path.relative_to(MONOREPO_ROOT),
            language=guess_language(project_path),
        )


def guess_language(project_path: Path) -> Language:
    """Guess the language of a project."""

    for file in project_path.iterdir():
        if file.name == "Cargo.toml":
            return Language.rust  # pragma: no cover
        if file.name == "package.json":
            return Language.javascript  # pragma: no cover
        if file.name == "pyproject.toml":
            return Language.python
    return Language.binary  # pragma: no cover
