# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from importlib.metadata import version

_python_project_name = "lrclibapi"
project = "LRCLib Python API"
copyright = "2023, Dr-Blank"
author = "Dr-Blank"
release = version(_python_project_name)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # to generate the docs from the docstrings
    "sphinx.ext.todo",  # to document the todos
    "sphinx.ext.viewcode",  # to generate the source code
    "sphinx.ext.autosectionlabel",  # to reference the sections with their titles
    "sphinx.ext.napoleon",  # to support the Google and NumPy docstrings
    "nbsphinx",  # to support the Jupyter notebooks
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
