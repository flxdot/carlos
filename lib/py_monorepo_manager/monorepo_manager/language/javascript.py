from typing import Literal

from pydantic import Field

from monorepo_manager.project import Language, Project


class JavascriptProject(Project):
    language: Literal[Language.javascript] = Field(
        Language.javascript,
        description="The programming language of the project.",
    )
