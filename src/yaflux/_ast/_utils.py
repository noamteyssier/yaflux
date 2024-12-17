import ast
import inspect
import textwrap


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
        raise ValueError(f"Could not parse function source: {e}") from e
