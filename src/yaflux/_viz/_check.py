import shutil


def _check_graphviz():
    """Check if graphviz and its executables are available"""
    try:
        import graphviz  # noqa

        return True
    except ImportError:
        return False


def _check_dot_exists():
    if not shutil.which("dot"):
        raise FileNotFoundError("Graphviz executables not found in PATH")
    return True
