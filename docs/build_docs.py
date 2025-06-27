#!/usr/bin/env python3
"""
Build script for Sphinx documentation with Python 3.13+ compatibility.
Works around the missing imghdr module in Python 3.13+.
"""

import sys
import types
import os
from pathlib import Path

def setup_imghdr_compatibility():
    """Create a minimal mock imghdr module for Python 3.13+ compatibility."""
    try:
        import imghdr  # type: ignore
        print("imghdr module already available")
    except ImportError:
        print("Creating imghdr compatibility shim for Python 3.13+")
        imghdr = types.ModuleType('imghdr')
        setattr(imghdr, 'what', lambda file, h=None: None)
        setattr(imghdr, 'tests', [])  # Empty list for tests
        sys.modules['imghdr'] = imghdr

def build_docs():
    """Build the Sphinx documentation."""
    setup_imghdr_compatibility()
    
    # Change to docs directory
    docs_dir = Path(__file__).parent
    os.chdir(docs_dir)
    
    # Import sphinx after setting up compatibility
    from sphinx.cmd.build import build_main
    
    # Build arguments
    args = [
        '-b', 'html',          # HTML builder
        '-E',                  # Don't use cached environment
        '.',                   # Source directory
        '_build/html'          # Output directory
    ]
    
    print(f"Building documentation with args: {args}")
    return build_main(args)

if __name__ == '__main__':
    sys.exit(build_docs())
