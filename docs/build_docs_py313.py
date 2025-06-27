#!/usr/bin/env python3
"""
Build script for Sphinx documentation with Python 3.13+ compatibility.
Works around the removed imghdr module in Python 3.13+.
"""

import os
import sys
import types
import importlib.util
from pathlib import Path

def monkey_patch_imghdr():
    """Create a minimal mock imghdr module for Python 3.13+ compatibility."""
    if importlib.util.find_spec('imghdr'):
        print("imghdr module already exists, no patching needed.")
        return
        
    print("Creating imghdr compatibility shim for Python 3.13+")
    
    # Create a mock imghdr module
    imghdr = types.ModuleType('imghdr')
    
    # Define the most essential functions
    def what(file, h=None):
        """Mock implementation of imghdr.what() that returns file extension."""
        if isinstance(file, str):
            return os.path.splitext(file)[1][1:]  # Return extension without dot
        return None
    
    # Add attributes to the mock module
    imghdr.what = what
    imghdr.tests = []  # Empty list that Sphinx will append to
    
    # Install the mock module
    sys.modules['imghdr'] = imghdr
    print("Mock imghdr module installed.")

def build_docs():
    """Build the Sphinx documentation."""
    # Apply the imghdr compatibility patch
    monkey_patch_imghdr()
    
    # Register MyST Parser explicitly
    try:
        import myst_parser
        print("Found MyST Parser version:", myst_parser.__version__)
    except ImportError:
        print("MyST Parser not found. Installing...")
        import subprocess
        subprocess.call([sys.executable, "-m", "pip", "install", "myst-parser>=1.0.0"])
        import myst_parser
        print("Installed MyST Parser version:", myst_parser.__version__)
    
    # Change to the docs directory
    docs_dir = Path(__file__).resolve().parent
    os.chdir(docs_dir)
    
    # Import the Sphinx build module
    from sphinx.cmd.build import build_main
    
    # Build HTML documentation
    args = [
        '-b', 'html',  # Build HTML format
        '-d', '_build/doctrees',  # Use a cache directory for doctrees
        '-c', '.',  # Use the current directory for configuration
        '-n',  # Do not use colors in output
        '.', '_build/html'  # Source dir and output dir
    ]
    
    print(f"Building documentation with Sphinx v5.0.0...")
    return build_main(args)

if __name__ == '__main__':
    sys.exit(build_docs())
