# yaflux/_loaders.py
from typing import Type, TypeVar

from ._base import Base
from ._results import ResultsLock
from ._yax import TarfileSerializer, YaxNotArchiveFileError

T = TypeVar("T", bound="Base")


def load(
    filepath: str,
    cls: Type[T] | None = None,
    no_results: bool = False,
    select: list[str] | str | None = None,
    exclude: list[str] | str | None = None,
) -> T:
    """
    Load analysis, attempting original class first, falling back to portable.

    Parameters
    ----------
    filepath : str
        Path to the analysis file
    cls : Type[T]
        The analysis class to attempt loading as
    no_results : bool, optional
        Only load metadata (yax format only), by default False
    select : Optional[List[str]], optional
        Only load specific results (yax format only), by default None
    exclude : Optional[List[str]], optional
        Skip specific results (yax format only), by default None
    """
    if TarfileSerializer.is_yaflux_archive(filepath):
        if cls is None:
            build_cls = Base
        else:
            build_cls = cls

        metadata, results = TarfileSerializer.load(
            filepath, no_results=no_results, select=select, exclude=exclude
        )

        try:
            # Load as original class
            return _load_file(filepath, build_cls, metadata, results)  # type: ignore
        except (AttributeError, ImportError, TypeError):
            # If loading as original class fails, load as `Base`
            return _load_file(filepath, Base, metadata, results)  # type: ignore

    else:
        raise YaxNotArchiveFileError(
            "The provided file is not a yax archive. Please provide a valid yax archive."
        )


def _load_file(
    filepath: str,
    cls: Type[T],
    metadata: dict,
    results: dict,
) -> T:
    """Inner function to load a file as a specific class."""

    # Create new instance
    instance = cls(parameters=metadata["parameters"])

    # Restore state
    with ResultsLock.allow_mutation():
        instance._completed_steps = set(metadata["completed_steps"])
        instance._step_ordering = metadata.get("step_ordering", [])
        instance._results._data = results
        instance._results._metadata = metadata["step_metadata"]

    return instance
