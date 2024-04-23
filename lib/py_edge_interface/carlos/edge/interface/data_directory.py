__all__ = ["DATA_DIRECTORY"]

from pathlib import Path


def find_data_directory(start_path=Path(__file__).parent):
    """Find the data directory for the package."""

    if (start_path / ".carlos_data" / ".gitkeep").exists():
        return start_path / ".carlos_data"

    if start_path == start_path.parent:  # pragma: no cover
        raise FileNotFoundError("Could not find data directory.")

    return find_data_directory(start_path.parent)


DATA_DIRECTORY = find_data_directory()
