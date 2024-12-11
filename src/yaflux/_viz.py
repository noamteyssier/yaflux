import shutil


def _check_graphviz():
    """Check if graphviz is available"""
    try:
        import graphviz  # noqa

        return True
    except ImportError:
        return False


def build_color_set(hex: str) -> tuple[str, str, str, str]:
    """Builds the color set given a base color"""
    complete_linecolor = f"{hex}FF"
    complete_fillcolor = f"{hex}80"  # 50% opacity
    incomplete_linecolor = f"{hex}10"  # 50% opacity
    incomplete_fillcolor = f"{hex}10"  # 10% opacity
    return (
        complete_linecolor,
        complete_fillcolor,
        incomplete_linecolor,
        incomplete_fillcolor,
    )


def visualize_dependencies(
    self,
    fontname: str = "Helvetica",
    fontsize: int = 11,
    rankdir: str = "LR",
    step_color: str = "#008000",  # darkgreen
    result_color: str = "#000080",  # darkblue
    flag_color: str = "#800000",  # darkred
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

    # Build color sets
    (
        step_complete_linecolor,
        step_complete_fillcolor,
        step_incomplete_linecolor,
        step_incomplete_fillcolor,
    ) = build_color_set(step_color)
    (
        result_complete_linecolor,
        result_complete_fillcolor,
        result_incomplete_linecolor,
        result_incomplete_fillcolor,
    ) = build_color_set(result_color)
    (
        flag_complete_linecolor,
        flag_complete_fillcolor,
        flag_incomplete_linecolor,
        flag_incomplete_fillcolor,
    ) = build_color_set(flag_color)

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
            fillcolor=step_complete_fillcolor
            if is_complete
            else step_incomplete_fillcolor,
            color=step_complete_linecolor if is_complete else step_incomplete_linecolor,
        )

        # Add nodes for results this step creates
        for result in method.creates:
            if result not in result_nodes:
                is_result_complete = hasattr(self.results, result)
                color = (
                    result_complete_linecolor
                    if is_result_complete
                    else result_incomplete_linecolor
                )
                fillcolor = (
                    result_complete_fillcolor
                    if is_result_complete
                    else result_incomplete_fillcolor
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

        # Add nodes for flags this step creates
        for flag in method.creates_flags:
            if flag not in result_nodes:
                is_flag_complete = hasattr(self.results, flag)
                color = (
                    flag_complete_linecolor
                    if is_flag_complete
                    else flag_incomplete_linecolor
                )
                fillcolor = (
                    flag_complete_fillcolor
                    if is_flag_complete
                    else flag_incomplete_fillcolor
                )
                dot.node(
                    flag,
                    f"flag{flag}",
                    style="filled",
                    shape="cds",
                    fillcolor=fillcolor,
                    color=color,
                )
                result_nodes.add(flag)

        # Add edges from requirements to step
        for req in method.requires:
            if req not in result_nodes:
                dot.node(
                    req,
                    req,
                    style="filled,rounded",
                    shape="box",
                    fillcolor=result_incomplete_fillcolor,
                    color=result_incomplete_linecolor,
                )
                result_nodes.add(req)

            # Edge from requirement to step
            dot.edge(
                req,
                f"step_{step_name}",
                "",
                color=result_complete_linecolor
                if is_complete
                else result_incomplete_linecolor,
            )

        # Add edges from required flags to step
        for flag in method.requires_flags:
            if flag not in result_nodes:
                dot.node(
                    flag,
                    flag,
                    style="filled,rounded",
                    shape="box",
                    fillcolor=flag_incomplete_fillcolor,
                    color=flag_incomplete_linecolor,
                )
                result_nodes.add(flag)

            # Edge from required flag to step
            dot.edge(
                flag,
                f"step_{step_name}",
                "",
                color=flag_complete_linecolor
                if is_complete
                else flag_incomplete_linecolor,
            )

        # Edges from step to its outputs
        for create in method.creates:
            dot.edge(
                f"step_{step_name}",
                create,
                "",
                color=step_complete_linecolor
                if is_complete
                else step_incomplete_linecolor,
            )

        # Edges from step to its flags
        for flag in method.creates_flags:
            dot.edge(
                f"step_{step_name}",
                flag,
                "",
                color=step_complete_linecolor
                if is_complete
                else step_incomplete_linecolor,
            )

    return dot
