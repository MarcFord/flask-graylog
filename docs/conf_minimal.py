# Configuration file for the Sphinx documentation builder.
# Minimal configuration for Sphinx 4.5.0 compatibility

import os
import sys
from pathlib import Path

# -- Path setup --------------------------------------------------------------
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# -- Project information -----------------------------------------------------
project = 'Flask Network Logging'
copyright = '2025, Marc Ford'
author = 'Marc Ford'
release = '1.0.0'
version = '1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Source file suffixes
source_suffix = {
    '.rst': None,
    '.md': 'myst_parser',
}

master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
html_theme = 'default'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_param = True
napoleon_use_rtype = True

# MyST parser settings
myst_enable_extensions = [
    "deflist",
    "tasklist", 
    "colon_fence",
]

# Mock imports for autodoc
autodoc_mock_imports = [
    'pygelf',
    'boto3',
    'botocore',
    'google.cloud.logging',
    'requests',
    'oci',
]

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'flask': ('https://flask.palletsprojects.com/en/2.0.x/', None),
}
