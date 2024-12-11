import shutil


def _check_graphviz():
    """Check if graphviz and its executables are available"""
    if not shutil.which("dot"):
        raise FileNotFoundError("Graphviz executables not found in PATH")
    return True
