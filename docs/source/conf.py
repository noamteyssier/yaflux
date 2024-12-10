import os
import sys

sys.path.insert(0, os.path.abspath("../../src/"))

project = "yaflux"
copyright = "2024, noam teyssier"
author = "noam teyssier"

# Extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "myst_parser",
    "numpydoc",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Configure MyST Parser
myst_enable_extensions = [
    "colon_fence",  # Enable ::: code blocks
    "deflist",  # Enable definition lists
    "dollarmath",  # Enable $ and $$ for math
    "fieldlist",  # Enable field lists
    "html_admonition",  # Enable !!! note blocks
    "html_image",  # Enable HTML image syntax
    "replacements",  # Enable text replacements
    "smartquotes",  # Enable smart quotes
    "tasklist",  # Enable task lists
]

# Configure Markdown specific settings
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}


# Set master doc as README.md instead of index.rst
master_doc = "index"

# Theming
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]

# Napoleon settings
napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None
