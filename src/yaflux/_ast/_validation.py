from ._assignment import validate_no_self_assignment
from ._results import validate_step_requirements


def validate_ast(
    func,
    requires: list[str],
) -> None:
    """Parse a function's AST and perform validation checks."""
    validate_step_requirements(func, requires)
    validate_no_self_assignment(func)
