from typing import Any

from .._metadata import Metadata
from ._error import FlagError, UnauthorizedMutationError
from ._lock import FlagLock, ResultsLock


class Results:
    """Dynamic container for analysis results.

    Attributes
    ----------
    _data : dict[str, Any]
        The results data. Indexed by the `creates` items in the step definition.

    _metadata: dict[str, Metadata]
        The metadata for each result. Indexed by the step name.
    """

    def __init__(self):
        self._data = {}
        self._metadata = {}

    def __getitem__(self, name):
        return self._data[name]

    def __getattr__(self, name):
        try:
            # Only try to get from _data if the attribute doesn't exist normally
            if name == "_data":
                raise AttributeError(f"No attribute named '{name}' exists")
            return self._data[name]
        except KeyError as exc:
            raise AttributeError(f"No result named '{name}' exists") from exc

    def __delattr__(self, name: str) -> None:
        if not ResultsLock.can_mutate():
            raise UnauthorizedMutationError(
                "Results can only be modified within a step decorator"
            )
        if name == "_data":
            raise AttributeError(f"Cannot delete attribute '{name}'")

        if not FlagLock.can_mutate():
            if name.startswith("_") and hasattr(self, name) and name != "_data":
                raise FlagError(f"Cannot delete flag once set: {name}")
        try:
            del self._data[name]
        except KeyError as exc:
            raise AttributeError(f"No result named '{name}' exists") from exc

    def __setattr__(self, name, value):
        if not ResultsLock.can_mutate():
            raise UnauthorizedMutationError(
                "Results can only be modified within a step decorator"
            )
        if name == "_data":
            object.__setattr__(self, name, value)

        if not FlagLock.can_mutate():
            if name.startswith("_") and hasattr(self, name) and name != "_data":
                raise FlagError(f"Cannot modify flag once set: {name}")
        else:
            self._data[name] = value

    def __dir__(self):
        return list(self._data.keys())

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self._data.keys())})"

    def __getstate__(self):
        return self._data

    def __setstate__(self, state):
        self._data = state

    def set_metadata(self, step_name: str, metadata: Metadata):
        """Set the metadata for a result."""
        self._metadata[step_name] = metadata

    def get_step_metadata(self, step_name: str) -> Metadata:
        """Get the metadata for a result."""
        return self._metadata[step_name]

    def get_step_results(self, step_name: str) -> dict[str, Any]:
        """Get the results for a step."""
        return {
            k: v
            for k, v in self._data.items()
            if k in self._metadata[step_name].creates
        }
