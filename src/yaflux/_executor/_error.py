class ExecutorMissingStartError(Exception):
    """Raised when there is no possible starting step in the analysis."""


class ExecutorCircularDependencyError(Exception):
    """Raised when a circular dependency is detected in the analysis steps."""


class ExecutorMissingTargetStepError(Exception):
    """Raised when the target step is not found in the analysis."""
