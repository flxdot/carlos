from carlos.edge.interface.data_directory import DATA_DIRECTORY


def test_data_directory():
    """This test ensures that the data directory is found correctly."""

    assert DATA_DIRECTORY.exists(), "Data directory should exist."
    assert DATA_DIRECTORY.is_dir(), "Data directory should be a directory."
    assert (
        DATA_DIRECTORY / ".gitkeep"
    ).exists(), "Data directory should contain a .gitkeep file."
