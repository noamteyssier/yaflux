import functools
import inspect
import time
from typing import Any, Callable, Optional, TypeVar, Union

from yaflux._base import Base
from yaflux._metadata import Metadata

T = TypeVar("T")


def _normalize_list(value: Optional[Union[list[str], str]]) -> list[str]:
    """Convert string or list input to normalized list."""
    if isinstance(value, str):
        return [value]
    return value or []


def _validate_instance_method(args: tuple) -> tuple[Base, tuple]:
    """Ensure the decorated function is called as instance method."""
    if not args or not isinstance(args[0], Base):
        raise ValueError("Analysis steps must be called as instance methods")
    return args[0], args[1:]


def _check_requirements(analysis: Base, requires: list[str]) -> None:
    """Validate that all required results exist."""
    missing = [req for req in requires if not hasattr(analysis._results, req)]
    if missing:
        raise ValueError(
            f"Missing required results: {missing}. Run required steps first."
        )


def _handle_existing_attributes(
    analysis: Base, creates: list[str], force: bool, panic: bool
) -> Optional[dict[str, Any]]:
    """Handle cases where results already exist."""
    for attr in creates:
        if hasattr(analysis._results, attr):
            if force:
                delattr(analysis._results, attr)
            elif panic:
                raise ValueError(f"Attribute {attr} already exists!")
            else:
                print(f"Attribute {attr} already exists - skipping step.")
                return {attr: getattr(analysis._results, attr) for attr in creates}
    return None


def _store_results(
    analysis: Base,
    creates: list[str],
    result: Any,
) -> None:
    """Store the function results in the analysis object."""

    # If the result is a dictionary, unpack it into the results object
    if isinstance(result, dict):
        # Assumes the keys of the dictionary are the names of the results
        for attr, value in result.items():
            setattr(analysis._results, attr, value)

    # If the result is a tuple, unpack it into the results object
    # Will assume that the order of the tuple is the same as the order of the creates list
    elif isinstance(result, tuple):
        if len(result) != len(creates):
            raise ValueError("Tuple result must have the same length as the creates list")

        for attr, value in zip(creates, result):
            setattr(analysis._results, attr, value)

    # Base base where the result is a single value
    elif result is not None and len(creates) == 1:
        setattr(analysis._results, creates[0], result)


def _store_metadata(
    analysis: Base,
    step_name: str,
    metadata: Metadata,
):
    """Store the step metadata within the analysis object."""
    analysis._results.set_metadata(step_name, metadata)


def _filter_valid_kwargs(func: Callable, kwargs: dict) -> dict:
    """Remove kwargs that aren't in the function signature."""
    sig = inspect.signature(func)
    return {k: v for k, v in kwargs.items() if k in sig.parameters}


def step(
    creates: Optional[Union[list[str], str]] = None,
    requires: Optional[Union[list[str], str]] = None,
) -> Callable:
    """Decorator to register analysis steps and their results.

    Parameters
    ----------
    creates : str | list[str] | None
        Names of the results this step creates
    requires : str | list[str] | None
        Names of the results this step requires
    """
    creates_list = _normalize_list(creates)
    requires_list = _normalize_list(requires)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Identify the step name
            step_name = func.__name__

            # Extract control flags
            force = kwargs.pop("force", False)
            panic_on_existing = kwargs.pop("panic_on_existing", False)

            # Setup and validation
            analysis_obj, remaining_args = _validate_instance_method(args)
            _check_requirements(analysis_obj, requires_list)

            # Handle existing results
            existing = _handle_existing_attributes(
                analysis_obj, creates_list, force, panic_on_existing
            )
            if existing is not None:
                return existing  # type: ignore

            # Filter valid kwargs
            valid_kwargs = _filter_valid_kwargs(func, kwargs)

            # Timestamp the start of the step
            start_time = time.time()

            # Execute the function
            result = func(analysis_obj, *remaining_args, **valid_kwargs)

            # Record the elapsed time
            elapsed = time.time() - start_time

            # Build the metadata object
            step_metadata = Metadata(
                creates=creates_list,
                requires=requires_list,
                timestamp=start_time,
                elapsed=elapsed,
                args=[str(arg) for arg in remaining_args],
                kwargs={k: str(v) for k, v in valid_kwargs.items()},
            )

            # Store the results
            _store_results(analysis_obj, creates_list, result)

            # Store the metadata
            _store_metadata(analysis_obj, step_name, step_metadata)

            # Mark completion
            analysis_obj._completed_steps.add(step_name)

            # Add to ordering if not already present
            if step_name not in analysis_obj._step_ordering:
                analysis_obj._step_ordering.append(step_name)

            return result

        # Store metadata
        wrapper.creates = creates_list  # type: ignore
        wrapper.requires = requires_list  # type: ignore
        return wrapper

    return decorator
