
class UnauthorizedMutationError(Exception):
    """Raised when attempting to modify results outside of a step decorator."""
    pass
