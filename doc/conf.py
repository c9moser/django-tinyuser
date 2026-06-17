# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
from pathlib import Path

import django

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django environment for autodoc
os.environ["DJANGO_SETTINGS_MODULE"] = "django_project.settings"
django.setup()


project = "django-tinyuser"
copyright = "2026, Christian Moser"
author = "Christian Moser"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "recommonmark",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_config = {
    "navbar_title": "django-tinyuser",
    "navbar_site_name": os.environ.get("SITE_NAME", "django-tinyuser"),
    "globaltoc_depth": os.environ.get("GLOBALTOC_DEPTH", 2),
}
html_static_path = ["_static"]
html_show_sourcelink = False

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
