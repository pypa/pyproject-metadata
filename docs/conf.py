# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import pyproject_metadata

# -- Project information -----------------------------------------------------

project = "pyproject-metadata"
copyright = "2021, Filipe Laíns"
author = "Filipe Laíns"

# The short X.Y version
version = pyproject_metadata.__version__
# The full version, including alpha/beta/rc tags
release = pyproject_metadata.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "packaging": ("https://packaging.pypa.io/en/latest/", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = []

source_suffix = [".rst", ".md"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"
html_title = f"pyproject-metadata {version}"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named 'default.css' will overwrite the builtin 'default.css'.
# html_static_path = ['_static']

autodoc_default_options = {
    "member-order": "bysource",
}

autoclass_content = "both"

# Type hints

always_use_bars_union = True
