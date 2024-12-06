import os
import pickle
from typing import Any

from ._results import Results


class BaseAnalysis:
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

    def __init__(self, parameters: Any):
        self._results = Results()
        self._completed_steps = set()
        self.parameters = parameters

    @property
    def results(self) -> Results:
        """Get the current analysis results."""
        return self._results

    @property
    def available_steps(self) -> list[str]:
        """List all available steps for the analysis."""
        return [
            name
            for name, method in self.__class__.__dict__.items()
            if hasattr(method, "creates")
        ]

    @property
    def completed_steps(self) -> list[str]:
        """List all completed steps for the analysis."""
        return list(self._completed_steps)

    def get_step_info(self, step_name: str):
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

    def save(self, filepath: str, force=False):
        """Save the `Analysis` object to a file using pickle."""
        if not force and os.path.exists(filepath):
            raise FileExistsError(f"File already exists: '{filepath}'")
        with open(filepath, "wb") as file:
            pickle.dump(self, file)

    @classmethod
    def load(cls, filepath: str):
        """Load an `Analysis` object from a file using pickle."""
        with open(filepath, "rb") as file:
            analysis = pickle.load(file)
        return analysis
