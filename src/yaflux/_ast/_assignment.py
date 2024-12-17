import ast

from ._error import AstSelfMutationError
from ._utils import get_function_node


def _get_leftmost_name(node) -> str | None:
    """Return the leftmost name in an assignment node."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return _get_leftmost_name(node.value)
    return None


def _build_assignment_name(node) -> str:
    """Return the full assignment path to the leftmost name in an assignment node.

    i.e.

    self.attr1.attr2.attr3 = ... => self.attr1.attr2.attr3
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return _build_assignment_name(node.value) + "." + node.attr
    else:
        raise ValueError("Unexpected node type in assignment")


class AssignmentVisitor(ast.NodeVisitor):
    """AST visitor that finds all assignments to self."""

    def __init__(self, mutates: list[str]):
        self.mutates = set(mutates)
        self.assignees: set[str] = set()

    def visit_Assign(self, node: ast.Assign) -> None:  # noqa
        # Check for pattern: self.{attr} = ...

        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Attribute)
            and _get_leftmost_name(node.targets[0]) == "self"
        ):
            assignment_name = _build_assignment_name(node.targets[0])

            if assignment_name.startswith("self.results"):
                attr = assignment_name.split("self.results.")[1]
                base_attr = attr.split(".")[0]
                if base_attr not in self.mutates:
                    self.assignees.add(assignment_name)

            # all non-results assignments are illegal regardless of `mutates`
            else:
                self.assignees.add(assignment_name)


def validate_no_self_assignment(func, mutates: list[str]) -> None:
    """Parse a function's AST and validate that self is not assigned to.

    Parameters
    ----------
    func : function
        The function to validate
    mutates : list[str]
        A list of attributes that are mutated by the function. If self is assigned to
        attributes outside of this list, an error is raised.
    """
    # Get the function AST node
    func_node = get_function_node(func)

    # Find assignments to self
    visitor = AssignmentVisitor(mutates=mutates)
    visitor.visit(func_node)

    if len(visitor.assignees) > 0:
        raise AstSelfMutationError(func.__name__, list(visitor.assignees))
