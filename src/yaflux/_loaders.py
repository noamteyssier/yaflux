# yaflux/_loaders.py
from typing import Type, TypeVar

from ._base import Base
from ._portable import Portable
from ._results import ResultsLock
from ._yax import TarfileSerializer

T = TypeVar("T", bound="Base")


def load_analysis(
    cls: Type[T],
    filepath: str,
    *,
    no_results: bool = False,
    select: list[str] | str | None = None,
    exclude: list[str] | str | None = None,
) -> T | Portable:
    """
    Load analysis, attempting original class first, falling back to portable.

    Parameters
    ----------
    cls : Type[T]
        The analysis class to attempt loading as
    filepath : str
        Path to the analysis file
    no_results : bool, optional
        Only load metadata (yax format only), by default False
    select : Optional[List[str]], optional
        Only load specific results (yax format only), by default None
    exclude : Optional[List[str]], optional
        Skip specific results (yax format only), by default None
    """
    # Try loading as yaflux archive first
    if TarfileSerializer.is_yaflux_archive(filepath):
        try:
            if cls is Portable:
                return load_portable(
                    filepath, no_results=no_results, select=select, exclude=exclude
                )

            metadata, results = TarfileSerializer.load(
                filepath, no_results=no_results, select=select, exclude=exclude
            )

            # Create new instance
            instance = cls(parameters=metadata["parameters"])

            # Restore state
            with ResultsLock.allow_mutation():
                instance._completed_steps = set(metadata["completed_steps"])
                instance._step_ordering = metadata.get("step_ordering", [])
                instance._results._data = results
                instance._results._metadata = metadata["step_metadata"]

            return instance
        except (AttributeError, ImportError, TypeError):
            # If loading as original class fails, fall back to portable
            return load_portable(
                filepath, no_results=no_results, select=select, exclude=exclude
            )

    else:
        raise ValueError(
            "Selective loading is only supported for .yax format. This appears to be a legacy pickle file."
        )


def load_portable(
    filepath: str,
    *,
    no_results: bool = False,
    select: list[str] | str | None = None,
    exclude: list[str] | str | None = None,
) -> Portable:
    """
    Load analysis in portable format, regardless of original class availability.

    Parameters
    ----------
    filepath : str
        Path to the analysis file
    no_results : bool, optional
        Only load metadata (yax format only), by default False
    select : Optional[List[str]], optional
        Only load specific results (yax format only), by default None
    exclude : Optional[List[str]], optional
        Skip specific results (yax format only), by default None
    """
    if TarfileSerializer.is_yaflux_archive(filepath):
        metadata, results = TarfileSerializer.load(
            filepath, no_results=no_results, select=select, exclude=exclude
        )

        # Restore state
        with ResultsLock.allow_mutation():
            # Create new instance
            instance = Portable(
                parameters=metadata["parameters"],
                results=results,
                completed_steps=metadata["completed_steps"],
                step_metadata=metadata["step_metadata"],
            )
            instance._step_ordering = metadata.get("step_ordering", [])

        return instance
    else:
        return ValueError("This is not a valid yax archive.")
