from ._error import MutabilityConflictError


def validate_incompatible_mutability(
    read_graph: dict[str, set[str]],
    write_graph: dict[str, set[str]],
    levels: dict[str, int],
) -> None:
    """Validate that no steps at the same level have incompatible mutability.

    Steps at the same level must not have any shared dependencies that are mutated.

    Parameters
    ----------
    read_graph : dict[str, set[str]]
        Graph of read dependencies indexed by step name.

    write_graph : dict[str, set[str]]
        Graph of write dependencies indexed by step name.

    levels : dict[str, int]
        Mapping of step names to their topological level.
    """
    # Invert the level mapping to get all steps at each level
    level_map = {}
    for step, level in levels.items():
        level_map.setdefault(level, []).append(step)

    for level, nodes in level_map.items():
        num_nodes = len(nodes)
        if num_nodes < 2:
            continue

        conflicts = []
        for idx in range(num_nodes):
            u = nodes[idx]
            for jdx in range(idx + 1, num_nodes):
                v = nodes[jdx]

                wr_overlap = write_graph[u] & read_graph[v]
                rw_overlap = read_graph[u] & write_graph[v]
                ww_overlap = write_graph[u] & write_graph[v]

                if wr_overlap or rw_overlap or ww_overlap:
                    overlaps = wr_overlap | rw_overlap | ww_overlap
                    conflicts.append((u, v, overlaps))

        if conflicts:
            raise MutabilityConflictError(level, conflicts)
