from pathlib import Path

import pytest

from .project import Project


class TestProject:
    @pytest.fixture(scope="class")
    def project(self, project_path: Path) -> Project:
        return Project.from_path(project_path)

    def test_properties(self, project: Project):
        assert project.is_library is True
        assert project.is_service != project.is_library
        assert project.abs_path == Path(__file__).parent.parent
