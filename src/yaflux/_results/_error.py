class UnauthorizedMutationError(Exception):
    """Raised when attempting to modify results outside of a step decorator."""

    pass


class FlagError(Exception):
    """Raised when attempting to modify a flag that has already been set."""

    pass
