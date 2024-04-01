"""This module contains the paths to the monorepo and its subdirectories."""

from pathlib import Path

__all__ = ["MONOREPO_ROOT", "SERVICES_PATH", "LIBRARIES_PATH", "METADATA_PATH"]


def find_monorepo_root(start_path: Path | None = None) -> Path:
    """Find the root of the monorepo."""
    if start_path is None:
        start_path = Path().cwd()

    if (start_path / ".git").exists():
        return start_path

    # If we're at the root of the filesystem, we can't go any higher
    if start_path == start_path.parent:  # pragma: no cover
        raise RuntimeError("Could not find the root of the monorepo.")

    return find_monorepo_root(start_path.parent)


MONOREPO_ROOT = find_monorepo_root()
SERVICES_PATH = MONOREPO_ROOT / "services"
LIBRARIES_PATH = MONOREPO_ROOT / "lib"

METADATA_PATH = MONOREPO_ROOT / ".monorepo_manager.yaml"
