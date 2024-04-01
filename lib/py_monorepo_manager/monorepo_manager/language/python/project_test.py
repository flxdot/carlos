from pathlib import Path

import pytest

from .project import PythonProject


class TestProject:
    @pytest.fixture(scope="class")
    def python_project(self, project_path: Path) -> PythonProject:
        return PythonProject.from_path(project_path)

    def test_properties(self, python_project: PythonProject):
        assert python_project.root_package_name == "monorepo_manager"
        assert python_project.monorepo_dependencies == ["lib/py_dev_dependencies"]
        assert python_project.python_version == "3.11"
