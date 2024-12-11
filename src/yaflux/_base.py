import os
import pickle
from typing import Any, Optional

from yaflux._results._lock import ResultsLock

from ._metadata import Metadata
from ._results import Results


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
        """Save the `Analysis` object to a file using pickle."""
        if not force and os.path.exists(filepath):
            raise FileExistsError(f"File already exists: '{filepath}'")
        with open(filepath, "wb") as file:
            pickle.dump(self, file)

    @classmethod
    def load(cls, filepath: str):
        """Load an `Analysis` object from a file using pickle."""
        with ResultsLock.allow_mutation():
            with open(filepath, "rb") as file:
                analysis = pickle.load(file)
        return analysis

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
        Base.visualize_dependencies = visualize_dependencies
except ImportError:
    pass  # Keep the stub method
