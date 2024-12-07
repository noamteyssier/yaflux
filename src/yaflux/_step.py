import functools
import inspect
from typing import Optional

from yaflux._base import BaseAnalysis


class AnalysisStep:
    """Decorator to register analysis steps and their results."""

    def __init__(
        self, creates: Optional[list[str]] = None, requires: Optional[list[str]] = None
    ):
        self.creates = creates or []
        self.requires = requires or []

    def _validate_requirements(self, analysis_obj):
        """Validate that required results (dependencies) exist."""
        missing = [
            req for req in self.requires if not hasattr(analysis_obj._results, req)
        ]
        if missing:
            raise ValueError(
                f"Missing required results: {missing}. Run required steps first."
            )

    def _validate_new_attributes(
        self, analysis_obj, force: bool = False, panic_on_existing: bool = False
    ) -> bool:
        """Validate that new attributes do not already exist.

        If force is True, delete the existing attributes.
        """
        for attr in self.creates:
            if hasattr(analysis_obj._results, attr):
                if force:
                    delattr(analysis_obj._results, attr)
                elif panic_on_existing:
                    raise ValueError(f"Attribute {attr} already exists!")
                else:
                    print(f"Attribute {attr} already exists - skipping step.")
                    return True
        return False

    def _store_results(self, analysis_obj, result):
        """Store the results of the analysis."""
        if isinstance(result, dict):
            for attr, value in result.items():
                setattr(analysis_obj._results, attr, value)
        elif result is not None and len(self.creates) == 1:
            setattr(analysis_obj._results, self.creates[0], result)

    def _get_results(self, analysis_obj):
        """Get the results of the analysis."""
        return {attr: getattr(analysis_obj._results, attr) for attr in self.creates}

    def _complete_step(self, analysis_obj, func):
        """Mark the step as completed."""
        analysis_obj._completed_steps.add(func.__name__)

    def __call__(self, func):
        """Register analysis steps and their results."""
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Determine if this is an instance method call
            if args and isinstance(args[0], BaseAnalysis):
                analysis_obj = args[0]
                remaining_args = args[1:]
            else:
                raise ValueError("Analysis steps must be called as instance methods")

            # Extract `force` parameter from kwargs if present
            force = kwargs.pop("force", False)
            panic_on_existing = kwargs.pop("panic_on_existing", False)

            # Filter out invalid kwargs
            valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

            # Validate requirements
            self._validate_requirements(analysis_obj)

            # New attributes before running the analysis
            skip = self._validate_new_attributes(
                analysis_obj, force=force, panic_on_existing=panic_on_existing
            )
            if skip:
                print("Skipping step.")
                return self._get_results(analysis_obj)

            # Run the analysis
            result = func(analysis_obj, *remaining_args, **valid_kwargs)

            # Register new attributes
            self._store_results(analysis_obj, result)

            # Mark the step as completed
            self._complete_step(analysis_obj, func)

            return result

        # Store metadata about the step
        wrapper.creates = self.creates  # type: ignore
        wrapper.requires = self.requires  # type: ignore
        return wrapper
