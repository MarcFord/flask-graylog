#!/usr/bin/env python3
"""
Build script for Sphinx documentation for Python 3.9
"""

import os
import sys
from pathlib import Path

def build_docs():
    """Build the Sphinx documentation."""
    # Change to the docs directory
    docs_dir = Path(__file__).parent / "docs"
    os.chdir(docs_dir)
    
    # Make sure we're using Python 3.9
    print(f"Python version: {sys.version}")
    
    # Set up source_suffix properly for MyST parser
    os.environ["SPHINX_SOURCE_SUFFIX"] = ".md=myst"
    
    # Import sphinx after verifying Python version
    from sphinx.cmd.build import main as sphinx_main
    
    # Build HTML documentation with direct arguments
    args = [
        "-b", "html",
        "-d", "_build/doctrees",
        ".",
        "_build/html"
    ]
    
    print(f"Building documentation with args: {args}")
    sphinx_main(args)

if __name__ == '__main__':
    build_docs()
