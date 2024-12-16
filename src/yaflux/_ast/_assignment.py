import ast

from ._error import AstSelfMutationError
from ._utils import get_function_node


class AssignmentVisitor(ast.NodeVisitor):
    """AST visitor that finds all assignments to self."""

    def __init__(self):
        self.assignees: set[str] = set()

    def visit_Assign(self, node: ast.Assign) -> None:
        # Check for pattern: self.{attr} = ...
        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Attribute)
            and isinstance(node.targets[0].value, ast.Name)
            and node.targets[0].value.id == "self"
        ):
            self.assignees.add(node.targets[0].attr)


def validate_no_self_assignment(func) -> None:
    """Parse a function's AST and validate that self is not assigned to."""

    # Get the function AST node
    func_node = get_function_node(func)

    # Find assignments to self
    visitor = AssignmentVisitor()
    visitor.visit(func_node)

    if len(visitor.assignees) > 0:
        raise AstSelfMutationError(func.__name__, list(visitor.assignees))
