"""This module contains the paths to the monorepo and its subdirectories."""

from pathlib import Path

__all__ = ["QMULUS_REPO_PATH", "SERVICES_PATH", "LIBRARIES_PATH", "METADATA_PATH"]


def find_monorepo_root(start_path: Path | None = None) -> Path:
    """Find the root of the Qmulus monorepo."""
    if start_path is None:
        start_path = Path().cwd()

    if (start_path / ".git").exists():
        return start_path

    # If we're at the root of the filesystem, we can't go any higher
    if start_path == start_path.parent:  # pragma: no cover
        raise RuntimeError("Could not find the root of the Qmulus monorepo.")

    return find_monorepo_root(start_path.parent)


QMULUS_REPO_PATH = find_monorepo_root()
SERVICES_PATH = QMULUS_REPO_PATH / "services"
LIBRARIES_PATH = QMULUS_REPO_PATH / "lib"

METADATA_PATH = QMULUS_REPO_PATH / ".monorepo_manager.yaml"
