from pathlib import Path

import pytest

from monorepo_manager.paths import QMULUS_REPO_PATH


@pytest.fixture(scope="session")
def project_path() -> Path:
    """Returns the path to this project to run the tests against."""

    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def own_project_key(project_path: Path) -> str:
    """Returns the key of this project to run the tests against."""

    return str(project_path.relative_to(QMULUS_REPO_PATH))
