from typing import Any

from ._metadata import Metadata
from ._results import Results, ResultsLock
from ._yax import TarfileSerializer


class Base:
    """Base class for analysis pipelines.

    This class provides a framework for defining and executing analysis pipelines.

    Parameters
    ----------
    parameters : Parameters
        The parameters for the analysis.

    Attributes
    ----------
    results : Results
        The current analysis results.

    available_steps : list[str]
        List all available steps for the analysis.

    completed_steps : list[str]
        List all completed steps for the analysis.
    """

    def __init__(self, parameters: Any | None = None):
        with ResultsLock.allow_mutation():  # Unlock during initialization
            self._results = Results()
        self._completed_steps = set()
        self._step_ordering = []  # Hidden attribute to store the order of steps
        self.parameters = parameters

        self._validate_dependency_graph()
        self._load_executor()

    @property
    def results(self) -> Results:
        """Get the current analysis results."""
        return self._results

    @property
    def available_steps(self) -> list[str]:
        """List all available steps for the analysis."""
        steps = []
        for cls in self.__class__.__mro__:
            for name, method in vars(cls).items():
                if hasattr(method, "creates") and name not in steps:
                    steps.append(name)
        return steps

    @property
    def completed_steps(self) -> list[str]:
        """List all completed steps for the analysis."""
        return list(self._completed_steps)

    def get_step_info(self, step_name: str) -> dict:
        """Get information about a specific analysis step."""
        method = getattr(self.__class__, step_name)
        if not method or not hasattr(method, "creates"):
            raise ValueError(f"No such analysis step: '{step_name}'")

        return {
            "name": step_name,
            "creates": method.creates,
            "requires": method.requires,
            "completed": step_name in self._completed_steps,
        }

    def get_step_metadata(self, step_name: str) -> Metadata:
        """Get the metadata for a specific analysis step."""
        if step_name not in self._completed_steps:
            raise ValueError(f"Step '{step_name}' has not been completed")
        return self._results.get_step_metadata(step_name)

    def get_step_results(self, step_name: str) -> Any:
        """Get the results for a specific analysis step."""
        if step_name not in self._completed_steps:
            raise ValueError(f"Step '{step_name}' has not been completed")
        return self._results.get_step_results(step_name)

    def metadata_report(self) -> list[dict[str, Any]]:
        """Return the metadata for all completed steps.

        The report will be in the order that the steps were completed.

        For steps which were run more than once their order will be in the order
        they were run the first time.
        """
        return [
            {
                "step": step,
                **self.get_step_metadata(step).to_dict(),
            }
            for step in self._step_ordering
        ]

    def save(self, filepath: str, force=False, compress=False):
        """Save the analysis to a file.

        If the filepath ends in .yax, saves in yaflux archive format.

        Parameters
        ----------
        filepath : str
            Path to save the analysis
        force : bool, optional
            Whether to overwrite existing file, by default False
        compress : bool, optional
            Whether to compress the file, by default False
        """
        if filepath.endswith(TarfileSerializer.EXTENSION):
            TarfileSerializer.save(filepath, self, force=force, compress=compress)
        elif filepath.endswith(TarfileSerializer.COMPRESSED_EXTENSION):
            TarfileSerializer.save(filepath, self, force=force, compress=True)
        else:
            TarfileSerializer.save(
                f"{filepath}.{TarfileSerializer.EXTENSION}",
                self,
                force=force,
                compress=compress,
            )

    @classmethod
    def load(
        cls,
        filepath: str,
        *,
        no_results: bool = False,
        select: list[str] | str | None = None,
        exclude: list[str] | str | None = None,
    ):
        """Load an analysis object from a file.

        Parameters
        ----------
        filepath : str
            Path to the analysis file. If .yax, load using yaflux archive format.
            Otherwise attempts to load as legacy pickle format.
        no_results : bool, optional
            Only load metadata (yaflux archive format only), by default False
        select : Optional[List[str]], optional
            Only load specific results (yaflux archive format only), by default None
        exclude : Optional[List[str]], optional
            Skip specific results (yaflux archive format only), by default None

        Returns
        -------
        Analysis
            The loaded analysis object

        Raises
        ------
        ValueError
            If selective loading is attempted with legacy pickle format
        """
        from ._loaders import load

        return load(
            filepath, cls, no_results=no_results, select=select, exclude=exclude
        )

    def _build_read_graph(self) -> dict[str, set[str]]:
        """Build the dependency graph of all steps in the analysis.

        This method builds a graph of all steps in the analysis and their dependencies.
        Dependencies are determined by union of `requires` and `mutates` attributes.
        This also includes flags.

        Returns
        -------
        dict[str, set[str]]
            The dependency graph as a dictionary of sets.
        """
        from ._graph import build_read_graph  # avoid circular import

        return build_read_graph(self)

    def _build_write_graph(self) -> dict[str, set[str]]:
        """Build the dependency graph of all steps in the analysis limited to mutations.

        This method builds a graph of all steps in the analysis and their dependencies.
        Dependencies are determined by the `mutates` attribute of each step.
        This does not include flags or read-only dependencies.

        Returns
        -------
        dict[str, set[str]]
            The dependency graph as a dictionary of sets.
        """
        from ._graph import build_write_graph  # avoid circular import

        return build_write_graph(self)

    def _compute_topological_levels(self, graph):
        """Calculate the topological levels of the dependency graph.

        Input is a graph of read dependencies (which includes write dependencies).

        Parameters
        ----------
        graph : dict[str, set[str]]
            The dependency graph as a dictionary of sets.

        Returns
        -------
        dict[str, int]
            A dictionary of step names and their topological levels.
        """
        from ._graph import compute_topological_levels

        return compute_topological_levels(graph)

    def _validate_incompatible_mutability(self, graph, wgraph, levels):
        """Validate the dependency graph for mutation conflicts.

        Raises
        ------
        ValueError
            If mutation conflicts are detected between steps at the same level
        """
        from ._graph import validate_incompatible_mutability

        validate_incompatible_mutability(graph, wgraph, levels)

    def _validate_dependency_graph(self):
        """Validate the dependency graph for mutation conflicts & circular dependencies.

        Raises
        ------
        yaflux.graph.CircularDependencyError
            If a circular dependency is detected in the graph
        yaflux.graph.MutabilityConflictError
            If a mutation conflict is detected in the graph
        """
        graph = self._build_read_graph()
        wgraph = self._build_write_graph()
        levels = self._compute_topological_levels(graph)
        self._validate_incompatible_mutability(graph, wgraph, levels)

    def _load_executor(self):
        """Load the executor engine for the analysis."""
        from ._executor import Executor  # Avoid circular import

        self._executor = Executor(self)

    def visualize_dependencies(self, *args, **kwargs):
        """Create a visualization of step dependencies.

        This is a stub that will be replaced with the actual visualization
        if graphviz is installed. Install with:

        ```bash
        pip install yaflux[viz]
        ```

        Raises
        ------
            ImportError: If graphviz is not installed.
        """
        raise ImportError(
            "graphviz package is required for visualization. "
            "Install with: pip install yaflux[viz]"
        )

    def execute(
        self,
        target_step: str | None = None,
        force: bool = False,
        panic_on_existing: bool = False,
    ) -> Any:
        """Execute analysis steps in dependency order up to target_step."""
        return self._executor.execute(
            target_step=target_step, force=force, panic_on_existing=panic_on_existing
        )

    def execute_all(self, force: bool = False, panic_on_existing: bool = False) -> None:
        """Execute all available steps in the analysis."""
        self._executor.execute_all(force=force, panic_on_existing=panic_on_existing)


try:
    from ._viz import _check_graphviz, visualize_dependencies

    if _check_graphviz():
        Base.visualize_dependencies = visualize_dependencies  # type: ignore
except ImportError:
    pass  # Keep the stub method
