from typing import Literal

from pydantic import Field

from monorepo_manager.project import Language, Project


class RustProject(Project):
    language: Literal[Language.rust] = Field(
        Language.rust,
        description="The programming language of the project.",
    )
