__all__ = ["PythonProject"]

import tomllib
from inspect import getdoc
from pathlib import Path
from typing import Literal, Any

from poetry.core.constraints.version import parse_constraint
from pydantic import BaseModel, Field, PrivateAttr, field_validator

from monorepo_manager.paths import MONOREPO_ROOT
from monorepo_manager.project import Language, Project


class Coverage(BaseModel):
    """Coverage settings for the project."""

    enabled: bool = Field(
        True,
        description="Whether coverage is enabled for the project.",
    )

    threshold: int = Field(
        100,
        description="The minimum coverage threshold for the project.",
    )


class Ruff(BaseModel):
    """Pylint settings for the project."""

    enabled: bool = Field(
        True,
        description="Whether ruff is enabled for the project.",
    )

    config: str = Field(
        "../../pyproject.toml",
        description="The ruff configuration file for the project.",
    )


class Mypy(BaseModel):
    """Mypy settings for the project."""

    enabled: bool = Field(
        True,
        description="Whether static type checking is enabled for the project.",
    )


class Deptry(BaseModel):
    """Deptry settings for the project."""

    enabled: bool = Field(
        False,
        description="Whether deptry checks are enabled for the project.",
    )

CiStep = dict[str, Any]


class CustomCiSteps(BaseModel):
    """Allows the user to define additional CI steps."""

    post_install_steps: list[CiStep] = Field(
        default_factory=list, description="Steps to run after the install step."
    )
    post_lint_steps: list[CiStep] = Field(
        default_factory=list, description="Steps to run after the lint step."
    )
    post_type_checking_steps: list[CiStep] = Field(
        default_factory=list, description="Steps to run after the mypy step."
    )
    post_test_steps: list[CiStep] = Field(
        default_factory=list, description="Steps to run after the test step."
    )

POETRY_VERSION = "1.7.1"


class PythonProject(Project):
    """A python project in the monorepo."""

    language: Literal[Language.python] = Field(
        Language.python,
        description="The programming language of the project.",
    )

    coverage: Coverage = Field(
        default_factory=Coverage,  # type: ignore
        description=getdoc(Coverage),
    )

    ruff: Ruff = Field(
        default_factory=Ruff,  # type: ignore
        description=getdoc(Ruff),
    )

    mypy: Mypy = Field(
        default_factory=Mypy,  # type: ignore
        description=getdoc(Mypy),
    )

    deptry: Deptry = Field(
        default_factory=Deptry,  # type: ignore
        description=getdoc(Deptry),
    )

    makefile: dict[str, list[str]] = Field(
        default_factory=dict,
        description="A dictionary of additional make targets to add to the Makefile."
        "The key is the name of the target, and the value is the command to run.",
    )

    @field_validator("makefile", mode="before")
    def validate_makefile(cls, v):
        """Ensure that the makefile is a dictionary of lists."""

        if not isinstance(v, dict):  # pragma: no cover
            raise TypeError("Invalid Project definition: makefile must be a dictionary")

        for target, command in v.items():
            if isinstance(command, str):  # pragma: no cover
                v[target] = [c.strip() for c in command.splitlines()]
        return v

    custom_ci_steps: CustomCiSteps = Field(
        default_factory=CustomCiSteps,
        description=getdoc(CustomCiSteps),
    )

    _pyproject_toml: dict = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)
        self._pyproject_toml = load_pyproject_toml(self.abs_path)

    @property
    def poetry_version(self) -> str:
        """Return the poetry version of the project."""

        return POETRY_VERSION

    @property
    def pyproject_toml(self) -> dict:
        """Return the pyproject.toml of the project."""

        return self._pyproject_toml

    @property
    def monorepo_dependencies(self) -> list[str]:
        """Return the dependencies of the project."""

        dependencies = []

        poetry_toml = self.pyproject_toml["tool"]["poetry"]

        toml_deps = list(poetry_toml["dependencies"].items())
        if "group" in poetry_toml:
            for group in poetry_toml["group"].values():
                if "dependencies" in group:
                    toml_deps += list(group["dependencies"].items())

        for name, version_spec in dict(toml_deps).items():
            if isinstance(version_spec, dict):
                if "path" in version_spec:  # pragma: no cover
                    rel_path = (
                        (self.abs_path / version_spec["path"])
                        .resolve()
                        .relative_to(MONOREPO_ROOT)
                    )
                    dependencies.append(rel_path.as_posix())

        return dependencies

    @property
    def dependency_cache_keys(self) -> list[str]:
        """Returns the key for the dependency cache."""

        hash_files = [f"./{self.path_from_root}/poetry.lock"]
        hash_files += [f"./{dep}/**/*.py" for dep in self.monorepo_dependencies]
        # some libraries contain test data. We need to invalidate the cache
        # in case the test data changes.
        hash_files += [f"./{dep}/**/*.sql" for dep in self.monorepo_dependencies]
        hash_files += [f"./{dep}/poetry.lock" for dep in self.monorepo_dependencies]
        return hash_files

    @property
    def package_name(self) -> str:
        """Return the name of the package."""

        return self.pyproject_toml["tool"]["poetry"]["name"]

    @property
    def root_package_name(  # pylint: disable=too-many-return-statements
        self,
    ) -> str:  # pragma: no cover
        """Return the name of the root package."""

        root_package_name = self.package_name.split(".")[0]

        if "-" in root_package_name:
            root_package_name = root_package_name.replace("-", "_")

        if (self.abs_path / root_package_name).is_dir():
            return root_package_name

        if (self.abs_path / "src" / root_package_name).is_dir():
            return f"src/{root_package_name}"

        # special case for module libraries
        if (self.abs_path / f"{root_package_name}.py").is_file():
            return root_package_name

        # todo: Do we really want to support those special cases for services?
        #  see: https://python-poetry.org/docs/cli/#new
        if not self.is_library:
            if (self.abs_path / "app").is_dir():
                return "app"
            if (self.abs_path / "src").is_dir():
                return "src"
            # special case for mkdocs projects
            # see: https://www.mkdocs.org/getting-started/
            if (self.abs_path / "docs").is_dir():
                return "docs"

        raise ValueError(
            f"Could not find root package for {self.abs_path}"
        )  # pragma: no cover

    @property
    def python_version(self) -> str:
        """Return the python version of the project."""

        version_constraint = parse_constraint(
            self.pyproject_toml["tool"]["poetry"]["dependencies"]["python"]
        )

        # Typing seems to be of in poetry. It actually as a `min` attribute.
        return version_constraint.min.text  # type: ignore


def load_pyproject_toml(project_path: Path):
    pyproject_toml_path = project_path / "pyproject.toml"

    if not pyproject_toml_path.exists():  # pragma: no cover
        raise FileNotFoundError(
            f"Could not find pyproject.toml at {pyproject_toml_path}"
        )

    with open(pyproject_toml_path, "rb") as f:
        data = tomllib.load(f)
    return data
