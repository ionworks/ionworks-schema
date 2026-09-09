import os
import sys

# -- Path setup --------------------------------------------------------------
# Must run before the ionworks_schema import below so a fresh clone without
# an editable install can build the docs via ``sphinx-build`` directly.

# Path for repository source so autodoc can import ionworks_schema.
sys.path.insert(0, os.path.abspath("../src"))

# Path for local Sphinx extensions
sys.path.append(os.path.abspath("./sphinxext/"))

import ionworks_schema as iws  # noqa: E402

# -- Project information -----------------------------------------------------

project = "Ionworks Schema"
copyright = "2026, Ionworks Technologies Inc"
author = "Ionworks Technologies Inc"

# Note: Both version and release are used in the build
version = iws.__version__
release = iws.__version__

# -- General configuration ---------------------------------------------------

extensions = [
    # Sphinx extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.doctest",
    # Third-party extensions
    "sphinx_design",
]
templates_path = ["_templates"]
source_suffix = [".rst"]
master_doc = "index"
language = "en"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Autodoc configuration --------------------------------------------------
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_member_order = "bysource"

# -- Intersphinx configuration ----------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
intersphinx_timeout = 5

# -- Options for HTML output -------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_logo = "source/_static/iw-icon.png"
html_static_path = ["source/_static"]
html_favicon = "source/_static/iw-icon.png"
html_permalinks_icon = "<span>¶</span>"

html_theme_options = {
    "external_links": [
        {"name": "Technical Guide", "url": "https://guide.ionworks.com/"},
    ],
}

# Base URL for the documentation
html_baseurl = "https://packages.docs.ionworks.com/ionworks-schema/"

# -- Suppress expected warnings ---------------------------------------------
# Pydantic v2 generates a lot of re-exported name references; don't noisy-fail
# on missing cross-references coming from intersphinx (pipeline site may not
# be live during this build).
nitpicky = False
suppress_warnings = ["ref.class", "ref.any"]
