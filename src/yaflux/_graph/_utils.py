from itertools import chain

from .._base import Base
from ._error import CircularDependencyError


def build_read_graph(analysis: Base) -> dict[str, set[str]]:
    """Build adjacency list of step dependencies.

    Includes both regular, flag, and mutation dependencies.

    Returns
    -------
    dict[str, set[str]]
        Graph indexed by step name with values as sets of dependent step names.
        An edge A -> B means step A depends on step B.
    """
    graph = {}

    # Map results/flags to the steps that create them
    creates_map = {}  # result/flag -> creating step
    for step_name in analysis.available_steps:
        method = getattr(analysis.__class__, step_name)
        for item in chain(method.creates, method.creates_flags):
            creates_map[item] = step_name

    # Build dependency graph
    for step_name in analysis.available_steps:
        method = getattr(analysis.__class__, step_name)

        # All dependencies: requires + requires_flags + mutates
        all_deps = chain(method.requires, method.requires_flags, method.mutates)

        # Find which step creates each dependency
        graph[step_name] = set()
        for dep in all_deps:
            if dep in creates_map:
                graph[step_name].add(creates_map[dep])

    return graph


def build_write_graph(analysis: Base) -> dict[str, set[str]]:
    """Build adjacency list of step dependencies.

    Includes **only** mutation dependencies.

    Returns
    -------
    dict[str, set[str]]
        Graph indexed by step name with values as sets of dependent step names.
        An edge A -> B means step A depends on step B.
    """
    graph = {}
    creates_map = {}
    for step_name in analysis.available_steps:
        method = getattr(analysis.__class__, step_name)
        for item in chain(method.creates, method.creates_flags):
            creates_map[item] = step_name

    for step_name in analysis.available_steps:
        method = getattr(analysis.__class__, step_name)
        graph[step_name] = set()
        for mut in method.mutates:
            if mut in creates_map:
                graph[step_name].add(creates_map[mut])

    return graph


def compute_topological_levels(graph: dict[str, set[str]]) -> dict[str, int]:
    """Compute the topological level of each step in the graph.

    A step's level is 1 + the maximum level of its dependencies.
    Steps with no dependencies have level 0.

    Parameters
    ----------
    graph : dict[str, set[str]]
        Graph indexed by step name with values as sets of dependent step names.
        An edge A -> B means step A depends on step B.

    Returns
    -------
    dict[str, int]
        Mapping of step names to their topological level.
    """
    levels = {}
    visited = set()

    def visit(node: str) -> int:
        # Check for circular dependencies
        if node in visited:
            raise CircularDependencyError(node)

        # Return memoized level if already computed
        if node in levels:
            return levels[node]

        visited.add(node)

        # Compute level as 1 + max level of dependencies
        level = 0 if not graph[node] else 1 + max(visit(dep) for dep in graph[node])
        levels[node] = level
        visited.remove(node)
        return level

    # Compute levels for all steps
    for node in graph:
        if node not in levels:
            visit(node)

    return levels
