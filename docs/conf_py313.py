#!/usr/bin/env python3
"""Simplified Sphinx configuration for Python 3.13+ compatibility."""

import os
import sys
from pathlib import Path

# -- Path setup --------------------------------------------------------------
# Add the project source to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# -- Project information -----------------------------------------------------
project = 'Flask Network Logging'
copyright = '2025, Marc Ford'
author = 'Marc Ford'

try:
    from flask_remote_logging import __version__
    release = __version__
    version = '.'.join(release.split('.')[:2])
except ImportError:
    release = '0.1.0-dev'
    version = '0.1'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# For MyST parser
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "tasklist",
]

# Set the source suffix for Markdown files
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# The master toctree document
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'flask': ('https://flask.palletsprojects.com/en/stable/', None),
    'boto3': ('https://boto3.amazonaws.com/v1/documentation/api/latest/', None),
}

# HTML context for templates
html_context = {
    'display_github': True,
    'github_user': 'MarcFord',
    'github_repo': 'flask-network-logging',
    'github_version': 'main',
    'conf_py_path': '/docs/',
}
