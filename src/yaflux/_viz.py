import shutil


def _check_graphviz():
    """Check if graphviz is available"""
    try:
        import graphviz  # noqa

        return True
    except ImportError:
        return False


def visualize_dependencies(
    self,
    fontname: str = "Helvetica",
    fontsize: int = 11,
    rankdir: str = "LR",
    complete_linecolor: str = "darkgreen",
    complete_fillcolor: str = "palegreen",
    incomplete_linecolor: str = "gray70",
    incomplete_fillcolor: str = "white",
    step_linecolor: str = "navy",
    step_fillcolor: str = "lightblue",
):
    """Create a clear visualization of step dependencies using Graphviz.

    Parameters
    ----------
    fontname : str, optional
        The font to use for text, by default "Helvetica"
    fontsize : int, optional
        The font size to use, by default 11
    rankdir : str, optional
        The direction of the graph layout, by default "LR"
    complete_linecolor : str, optional
        The color of edges for completed steps, by default "darkgreen"
    complete_fillcolor : str, optional
        The fill color for nodes of completed steps, by default "palegreen"
    incomplete_linecolor : str, optional
        The color of edges for incomplete steps, by default "gray70"
    incomplete_fillcolor : str, optional
        The fill color for nodes of incomplete steps, by default "white"
    step_linecolor : str, optional
        The color of edges for step nodes, by default "navy"
    step_fillcolor : str, optional
        The fill color for step nodes, by default "lightblue"

    Returns
    -------
    graphviz.Digraph
        The rendered graph object

    Examples
    --------
    >>> import yaflux as yf
    >>>
    >>> class MyAnalysis(yf.Base):
    >>>     @yf.step(creates="a")
    >>>     def step_a(self):
    >>>         return 42
    >>>
    >>>     @yf.step(creates="b", requires="a")
    >>>     def step_b(self):
    >>>         return 42
    >>>
    >>>     @yf.step(creates="c", requires=["a", "b"])
    >>>     def step_c(self):
    >>>         return 42
    >>>
    >>> analysis = MyAnalysis()
    >>>
    >>> # Visualize the dependencies
    >>> analysis.visualize_dependencies()
    >>>
    >>> # Save the visualization to a file
    >>> dot = analysis.visualize_dependencies()
    >>> dot.render('dependencies.pdf')
    """
    if not _check_graphviz():
        raise ImportError(
            "Graphviz is required for this method.\n"
            "Install with `pip install yaflux[viz]`"
        )

    # Checks if `dot` in the environment
    if not shutil.which("dot"):
        raise FileNotFoundError("Graphviz executables not found in PATH")

    from graphviz import Digraph

    dot = Digraph(comment="Analysis Dependencies")
    dot.attr(rankdir=rankdir)

    # Set some global attributes for nicer appearance
    dot.attr("node", fontname=fontname)
    dot.attr("edge", fontname=fontname)
    dot.attr("graph", fontsize=str(fontsize))

    # Track all nodes to avoid duplicates
    result_nodes = set()

    # Add all nodes and edges
    for step_name in self.available_steps:
        method = getattr(self.__class__, step_name)
        is_complete = step_name in self.completed_steps

        # Add step node
        dot.node(
            f"step_{step_name}",
            step_name,
            shape="box",
            style="filled",
            fillcolor=step_fillcolor,
            color=step_linecolor if is_complete else incomplete_linecolor,
        )

        # Add nodes for results this step creates
        for result in method.creates:
            if result not in result_nodes:
                is_result_complete = hasattr(self.results, result)
                color = (
                    complete_linecolor if is_result_complete else incomplete_linecolor
                )
                fillcolor = (
                    complete_fillcolor if is_result_complete else incomplete_fillcolor
                )
                dot.node(
                    result,
                    result,
                    style="filled,rounded",
                    shape="box",
                    fillcolor=fillcolor,
                    color=color,
                )
                result_nodes.add(result)

        # Add edges from requirements to step and step to creates
        for req in method.requires:
            if req not in result_nodes:
                dot.node(
                    req,
                    req,
                    style="filled,rounded",
                    shape="box",
                    fillcolor=incomplete_fillcolor,
                    color=incomplete_linecolor,
                )
                result_nodes.add(req)

            # Edge from requirement to step
            dot.edge(
                req,
                f"step_{step_name}",
                "",
                color=complete_linecolor if is_complete else incomplete_linecolor,
            )

        # Edges from step to its outputs
        for create in method.creates:
            dot.edge(
                f"step_{step_name}",
                create,
                "",
                color=complete_linecolor if is_complete else incomplete_linecolor,
            )

    return dot
