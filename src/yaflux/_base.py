from typing import Any, Optional

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

    def __init__(self, parameters: Optional[Any] = None):
        with ResultsLock.allow_mutation():  # Unlock during initialization
            self._results = Results()
        self._completed_steps = set()
        self._step_ordering = []  # Hidden attribute to store the order of performed steps
        self.parameters = parameters

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

    def save(self, filepath: str, force=False):
        """Save the analysis to a file.

        If the filepath ends in .yax, saves in yaflux archive format.

        Parameters
        ----------
        filepath : str
            Path to save the analysis
        force : bool, optional
            Whether to overwrite existing file, by default False
        """
        if filepath.endswith(TarfileSerializer.EXTENSION):
            TarfileSerializer.save(filepath, self, force)
        else:
            TarfileSerializer.save(
                f"{filepath}.{TarfileSerializer.EXTENSION}", self, force
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
            Path to the analysis file. If it ends in .yax, loads using yaflux archive format.
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

    def visualize_dependencies(self, *args, **kwargs):
        """Create a visualization of step dependencies.

        This is a stub that will be replaced with the actual visualization
        if graphviz is installed. Install with:

        ```bash
        pip install yaflux[viz]
        ```

        Raises:
            ImportError: If graphviz is not installed.
        """
        raise ImportError(
            "graphviz package is required for visualization. "
            "Install with: pip install yaflux[viz]"
        )


try:
    from ._viz import _check_graphviz, visualize_dependencies

    if _check_graphviz():
        Base.visualize_dependencies = visualize_dependencies  # type: ignore
except ImportError:
    pass  # Keep the stub method
