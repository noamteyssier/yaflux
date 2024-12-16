class AstUndeclaredUsageError(Exception):
    """Raised when an undeclared variable is used in the AST."""

    def __init__(self, func_name: str, undeclared: list[str]):
        self.func_name = func_name
        self.undeclared = undeclared
        super().__init__(
            f"Function {func_name} uses undeclared variables: {undeclared}"
            + "Add these variables to the requires list in the step decorator."
        )


class AstSelfMutationError(Exception):
    """Raised when self is mutated in a function."""

    def __init__(self, func_name: str, mutated: list[str]):
        self.func_name = func_name
        self.mutated = mutated
        super().__init__(
            f"Function {func_name} mutates self: {mutated}"
            + "Mutating self is not allowed in step functions."
        )
