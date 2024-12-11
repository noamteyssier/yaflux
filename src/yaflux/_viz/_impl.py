from typing import Literal, Set

from ._check import _check_dot_exists, _check_graphviz
from ._style import GraphConfig


def add_node(
    dot,
    node_id: str,
    node_type: Literal["step", "result", "flag"],
    is_complete: bool,
    config: GraphConfig,
) -> None:
    """Add a node to the graph with appropriate styling"""
    style = config.node_styles[node_type]
    colors = getattr(config, f"{node_type}_colors")

    dot.node(
        f"{node_type}_{node_id}",
        f"{style.prefix}{node_id}" if style.prefix else node_id,
        shape=style.shape,
        style=style.style,
        fillcolor=colors["complete_fill"] if is_complete else colors["incomplete_fill"],
        color=colors["complete_line"] if is_complete else colors["incomplete_line"],
    )


def add_edge(
    dot,
    from_node: str,
    to_node: str,
    color_set: dict[str, str],
    is_complete: bool,
    from_node_type: Literal["step", "result", "flag"],
    to_node_type: Literal["step", "result", "flag"],
) -> None:
    """Add an edge to the graph with appropriate styling"""
    dot.edge(
        f"{from_node_type}_{from_node}",
        f"{to_node_type}_{to_node}",
        "",
        color=color_set["complete_line"]
        if is_complete
        else color_set["incomplete_line"],
    )


def visualize_dependencies(self, **kwargs):
    """Create a clear visualization of step dependencies using Graphviz.

    Parameters
    ----------
    **kwargs : dict
        Configuration options passed to GraphConfig

    Returns
    -------
    graphviz.Digraph
        The rendered graph object
    """
    if not _check_graphviz():
        raise ImportError(
            "Graphviz is required for this method.\n"
            "Install with `pip install yaflux[viz]`"
        )
    else:
        from graphviz import Digraph
    _check_dot_exists()

    # Get configuration options
    config = GraphConfig(**kwargs)

    # Create the graph object
    dot = Digraph(comment="Analysis Dependencies")

    # Set global attributes
    dot.attr(rankdir=config.rankdir)
    dot.attr("node", fontname=config.fontname)
    dot.attr("edge", fontname=config.fontname)
    dot.attr("graph", fontsize=str(config.fontsize))

    result_nodes: Set[str] = set()

    # Get all available steps including inherited ones
    available_steps = {}
    for cls in self.__class__.__mro__:
        for name, method in vars(cls).items():
            if hasattr(method, "creates") and name not in available_steps:
                available_steps[name] = method

    # Add all nodes and edges
    for step_name, method in available_steps.items():
        is_step_complete = step_name in self.completed_steps

        # Add step node
        add_node(dot, step_name, "step", is_step_complete, config)

        # Add result nodes and edges
        for result in method.creates:
            if result not in result_nodes:
                is_result_complete = hasattr(self.results, result)
                add_node(dot, result, "result", is_result_complete, config)
                result_nodes.add(result)
            add_edge(
                dot,
                step_name,
                result,
                config.step_colors,
                is_step_complete,
                "step",
                "result",
            )

        # Add flag nodes and edges
        for flag in method.creates_flags:
            if flag not in result_nodes:
                is_flag_complete = hasattr(self.results, flag)
                add_node(dot, flag, "flag", is_flag_complete, config)
                result_nodes.add(flag)
            add_edge(
                dot,
                step_name,
                flag,
                config.step_colors,
                is_step_complete,
                "step",
                "flag",
            )

        # Add requirement edges
        for req in method.requires:
            if req not in result_nodes:
                is_req_complete = hasattr(self.results, req)
                add_node(dot, req, "result", is_req_complete, config)
                result_nodes.add(req)
            add_edge(
                dot,
                req,
                step_name,
                config.result_colors,
                is_step_complete,
                "result",
                "step",
            )

        # Add flag requirement edges
        for flag in method.requires_flags:
            if flag not in result_nodes:
                is_flag_complete = hasattr(self.results, flag)
                add_node(dot, flag, "flag", is_flag_complete, config)
                result_nodes.add(flag)
            add_edge(
                dot,
                flag,
                step_name,
                config.flag_colors,
                is_step_complete,
                "flag",
                "step",
            )

    return dot
