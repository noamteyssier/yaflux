import types
from typing import Any, Dict, List

from ._base import Base
from ._results import Results


class Portable(Base):
    """
    A self-contained analysis container that can be unpickled without the original class.
    Preserves the step metadata and results while dropping the actual implementation.
    """

    def __init__(
        self,
        parameters: Any,
        results: Dict[str, Any],
        completed_steps: List[str],
        step_metadata: Dict[str, Dict[str, List[str]]],
    ):
        # Initialize Base with parameters
        super().__init__(parameters)

        # Override Results with provided data
        self._results = Results()
        self._results._data = results

        # Set completed steps
        self._completed_steps = set(completed_steps)

        # Store step metadata
        self._step_metadata = step_metadata

        # Create placeholder methods for each original step
        for step_name, metadata in step_metadata.items():
            placeholder = self._create_placeholder(step_name, metadata)
            setattr(self, step_name, types.MethodType(placeholder, self))

    def _create_placeholder(self, name: str, metadata: Dict[str, List[str]]):
        """Create a placeholder method that raises NotImplementedError."""

        def placeholder(self):
            raise NotImplementedError(
                f"Step '{name}' is a placeholder. This is a portable snapshot "
                f"that contains only results and metadata.\n"
                f"creates: {metadata['creates']}\n"
                f"requires: {metadata['requires']}"
            )

        return placeholder

    @property
    def available_steps(self) -> List[str]:
        """List of all steps that were available in original analysis."""
        return list(self._step_metadata.keys())

    @classmethod
    def from_analysis(cls, analysis: Base) -> "Portable":
        """Create a portable version from an existing analysis."""
        metadata = {}
        for name in analysis.available_steps:
            method = getattr(analysis.__class__, name)
            metadata[name] = {"creates": method.creates, "requires": method.requires}

        return cls(
            parameters=analysis.parameters,
            results=analysis.results._data,
            completed_steps=analysis.completed_steps,
            step_metadata=metadata,
        )

    @classmethod
    def load(cls, filepath: str) -> "Portable":
        """Load a portable analysis from a file.

        Overrides the base class by explicitly loading as Portable.
        """
        from ._loaders import load_analysis

        return load_analysis(Portable, filepath)
