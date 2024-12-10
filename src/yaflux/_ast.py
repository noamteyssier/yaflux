import ast
import inspect
import textwrap


class ResultsAttributeVisitor(ast.NodeVisitor):
    """AST visitor that finds all self.results attribute accesses."""

    def __init__(self):
        self.accessed_attrs: set[str] = set()

    def visit_Attribute(self, node: ast.Attribute) -> None:
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


def get_function_node(func) -> ast.FunctionDef:
    """Extract the FunctionDef node from a function's source code."""
    # Get the source lines
    source_lines = inspect.getsource(func).splitlines()

    # Find the first line that starts with 'def'
    for i, line in enumerate(source_lines):
        if line.lstrip().startswith("def "):
            # Join from this line onwards
            func_source = "\n".join(source_lines[i:])
            # Dedent the source code to remove any indentation
            func_source = textwrap.dedent(func_source)
            break
    else:
        raise ValueError("Could not find function definition")

    # Parse the function source
    try:
        tree = ast.parse(func_source)
        if not isinstance(tree.body[0], ast.FunctionDef):
            raise ValueError("Could not parse function definition")
        return tree.body[0]
    except SyntaxError as e:
        raise ValueError(f"Could not parse function source: {e}")


def validate_results_usage(
    func_node: ast.FunctionDef, requires: list[str]
) -> tuple[list[str], list[str]]:
    """
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
    """
    Parse a function's AST and validate all self.results accesses.

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
        raise ValueError(
            f"Accessing undeclared results attributes in {func_name}: {undeclared}. "
            f"Add these to the 'requires' parameter of the @step decorator."
        )

    # Warn about unused requirements
    if unused:
        import warnings

        warnings.warn(
            f"The following required attributes are never accessed in {func_name}: {unused}. "
            f"Consider removing them from the 'requires' parameter.",
            stacklevel=2,
        )
