import functools
import inspect
from typing import Any, Callable, Optional, TypeVar

from yaflux._base import BaseAnalysis

T = TypeVar('T')

def _normalize_list(value: Optional[list[str] | str]) -> list[str]:
    """Convert string or list input to normalized list."""
    if isinstance(value, str):
        return [value]
    return value or []

def _validate_instance_method(args: tuple) -> tuple[BaseAnalysis, tuple]:
    """Ensure the decorated function is called as instance method."""
    if not args or not isinstance(args[0], BaseAnalysis):
        raise ValueError("Analysis steps must be called as instance methods")
    return args[0], args[1:]

def _check_requirements(analysis: BaseAnalysis, requires: list[str]) -> None:
    """Validate that all required results exist."""
    missing = [req for req in requires if not hasattr(analysis._results, req)]
    if missing:
        raise ValueError(f"Missing required results: {missing}. Run required steps first.")

def _handle_existing_attributes(
    analysis: BaseAnalysis,
    creates: list[str],
    force: bool,
    panic: bool
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
    analysis: BaseAnalysis,
    creates: list[str],
    result: Any
) -> None:
    """Store the function results in the analysis object."""
    if isinstance(result, dict):
        for attr, value in result.items():
            setattr(analysis._results, attr, value)
    elif result is not None and len(creates) == 1:
        setattr(analysis._results, creates[0], result)

def _filter_valid_kwargs(func: Callable, kwargs: dict) -> dict:
    """Remove kwargs that aren't in the function signature."""
    sig = inspect.signature(func)
    return {k: v for k, v in kwargs.items() if k in sig.parameters}

def step(
    creates: Optional[list[str] | str] = None,
    requires: Optional[list[str] | str] = None
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
            # Extract control flags
            force = kwargs.pop("force", False)
            panic_on_existing = kwargs.pop("panic_on_existing", False)

            # Setup and validation
            analysis_obj, remaining_args = _validate_instance_method(args)
            _check_requirements(analysis_obj, requires_list)

            # Handle existing results
            existing = _handle_existing_attributes(
                analysis_obj,
                creates_list,
                force,
                panic_on_existing
            )
            if existing is not None:
                return existing  # type: ignore

            # Execute and store
            valid_kwargs = _filter_valid_kwargs(func, kwargs)
            result = func(analysis_obj, *remaining_args, **valid_kwargs)
            _store_results(analysis_obj, creates_list, result)

            # Mark completion
            analysis_obj._completed_steps.add(func.__name__)
            return result

        # Store metadata
        wrapper.creates = creates_list  # type: ignore
        wrapper.requires = requires_list  # type: ignore
        return wrapper

    return decorator
