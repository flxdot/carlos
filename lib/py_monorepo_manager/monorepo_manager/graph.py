"""This module contains some utility functions to resolve graph dependencies."""

__all__ = [
    "depth_first_search",
]

from collections.abc import Hashable, Iterable, Mapping
from typing import TypeVar

GraphNode = TypeVar("GraphNode", str, int, Hashable)


def depth_first_search(
    graph: Mapping[GraphNode, Iterable[GraphNode]],
    start: GraphNode | None = None,
    visited: list[GraphNode] | None = None,
) -> list[GraphNode]:
    """Return a list of nodes in depth-first-search order. The order is reversed to
    match the order of the dependencies.

    :param graph: The graph to traverse.
    :param start: The node to start the traversal from.
    :param visited: A list of already visited nodes.
    :return: A list of nodes in depth-first-search order.
    """
    if visited is None:
        visited = []
    if start is None:
        for node in graph:
            depth_first_search(graph=graph, start=node, visited=visited)
        return visited

    if start not in visited:
        for node in graph[start]:
            depth_first_search(graph=graph, start=node, visited=visited)
        visited.append(start)

    return visited
