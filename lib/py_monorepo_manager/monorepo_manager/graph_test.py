import pytest

from .graph import depth_first_search


@pytest.mark.parametrize(
    "graph, start, expected",
    [
        pytest.param(
            {
                "1": [],
                "a": ["b", "c"],
                "b": ["d"],
                "c": ["d"],
                "d": ["e"],
                "e": [],
                "f": [],
            },
            None,
            ["1", "e", "d", "b", "c", "a", "f"],
            id="simple-graph",
        ),
    ],
)
def test_depth_first_search(
    graph: dict[str, list[str]], start: str | None, expected: list[str]
):
    """Test the depth_first_search() function."""
    assert depth_first_search(graph, start) == expected
