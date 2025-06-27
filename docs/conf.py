# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document) are in another directory, add these
# directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Flask Network Logging'
copyright = '2025, Marc Ford'
author = 'Marc Ford'

# The full version, including alpha/beta/rc tags
try:
    from flask_remote_logging import __version__
    release = __version__
    version = '.'.join(release.split('.')[:2])  # Short X.Y version
except ImportError:
    release = '0.1.0-dev'
    version = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'myst_parser',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix(es) of source filenames.
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'default'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------

# -- Options for autodoc ----------------------------------------------------
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# -- Options for autosummary ------------------------------------------------
autosummary_generate = True

# -- Options for napoleon ----------------------------------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# -- Options for intersphinx -------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'flask': ('https://flask.palletsprojects.com/en/2.3.x/', None),
    'boto3': ('https://boto3.amazonaws.com/v1/documentation/api/latest/', None),
}

# -- Options for todo extension ----------------------------------------------
todo_include_todos = True

# -- Options for MyST parser ------------------------------------------------
myst_enable_extensions = [
    "deflist",
    "tasklist",
    "colon_fence",
]

# -- Custom configuration ---------------------------------------------------

# Mock modules that might not be available during documentation build
autodoc_mock_imports = [
    'pygelf',
    'boto3',
    'botocore',
    'google.cloud.logging',
    'requests',
    'oci',
]

# HTML context for templates
html_context = {
    'display_github': True,
    'github_user': 'MarcFord',
    'github_repo': 'flask-network-logging',
    'github_version': 'main',
    'conf_py_path': '/docs/',
}

# Add custom CSS if needed
def setup(app):
    """Setup function for Sphinx app."""
    pass

# Workaround for Python 3.13+ imghdr removal
# This prevents the error related to sphinx.builders.epub3 attempting to import imghdr
import sys
if sys.version_info >= (3, 13):
    exclude_patterns.append('**/*.epub')
    epub_exclude = True
    
    # Monkey patch for Sphinx's use of imghdr
    try:
        import imghdr
    except ImportError:
        import os
        sys.modules['imghdr'] = type('imghdr', (), {
            'what': lambda f, h=None: os.path.splitext(f)[1][1:] if isinstance(f, str) else None
        })
        
    # Remove epub builder if present
    if 'sphinx.builders.epub3' in sys.modules:
        del sys.modules['sphinx.builders.epub3']
