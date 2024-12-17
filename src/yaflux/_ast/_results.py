import ast

from ._error import AstUndeclaredUsageError
from ._utils import get_function_node


class ResultsAttributeVisitor(ast.NodeVisitor):
    """AST visitor that finds all self.results attribute accesses."""

    def __init__(self):
        self.accessed_attrs: set[str] = set()

    def visit_Attribute(self, node: ast.Attribute) -> None:  # noqa: N802
        """Visit attribute access nodes in the AST."""
        # Check for pattern: self.results.{attr}
        if (
            isinstance(node.value, ast.Attribute)
            and isinstance(node.value.value, ast.Name)
            and node.value.value.id == "self"
            and node.value.attr == "results"
        ):
            self.accessed_attrs.add(node.attr)
        self.generic_visit(node)


def validate_results_usage(
    func_node: ast.FunctionDef, requires: list[str]
) -> tuple[list[str], list[str]]:
    """Validate all accesses are declared in requires.

    Validate that all self.results.{attr} accesses are declared in requires
    and all requires are actually used.

    Parameters
    ----------
    func_node : ast.FunctionDef
        The AST node of the function definition
    requires : list[str]
        List of required attributes declared in the step decorator

    Returns
    -------
    tuple[list[str], list[str]]
        First list contains undeclared attributes that are used
        Second list contains declared attributes that are not used
    """
    visitor = ResultsAttributeVisitor()
    visitor.visit(func_node)

    # Find attributes used but not declared
    undeclared = [attr for attr in visitor.accessed_attrs if attr not in requires]

    # Find attributes declared but not used
    unused = [attr for attr in requires if attr not in visitor.accessed_attrs]

    return undeclared, unused


def validate_step_requirements(func, requires: list[str]) -> None:
    """Parse a function's AST and validate all self.results accesses.

    Parameters
    ----------
    func : Callable
        The function to validate
    requires : list[str]
        List of required attributes declared in the step decorator

    Raises
    ------
    ValueError
        If any self.results attributes are accessed but not declared in requires
    Warning
        If any requires attributes are declared but not used
    """
    # Get the function AST node
    func_node = get_function_node(func)

    # Validate usage
    undeclared, unused = validate_results_usage(func_node, requires)

    # Get the function name
    func_name = func.__name__

    # Raise error for undeclared attributes
    if undeclared:
        raise AstUndeclaredUsageError(func_name, undeclared)

    # Warn about unused requirements
    if unused:
        import warnings

        warnings.warn(
            "The following required attributes are never accessed in "
            + f"{func_name}: {unused}. "
            + "Consider removing them from the 'requires' parameter.",
            stacklevel=2,
        )
