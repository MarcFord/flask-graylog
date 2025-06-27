#!/usr/bin/env python3
"""
Build script for Sphinx documentation with Python 3.13+ compatibility.
Works around the missing imghdr module in Python 3.13+ and extension issues.
"""

import sys
import os
import types
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

def patch_sphinx_config():
    """Patch sphinx config to remove incompatible extensions."""
    conf_path = Path(__file__).parent / "conf.py"
    with open(conf_path, "r") as f:
        content = f.read()
    
    # Remove problematic extensions (applehelp, devhelp, qthelp, htmlhelp)
    if "sphinxcontrib.applehelp" in content:
        print("Removing incompatible extensions from conf.py temporarily")
        replacements = [
            ("sphinxcontrib.applehelp", "# sphinxcontrib.applehelp"),
            ("sphinxcontrib.devhelp", "# sphinxcontrib.devhelp"),
            ("sphinxcontrib.qthelp", "# sphinxcontrib.qthelp"),
            ("sphinxcontrib.htmlhelp", "# sphinxcontrib.htmlhelp")
        ]
        for old, new in replacements:
            content = content.replace(old, new)
        
        # Write temp config
        temp_conf = conf_path.with_name("conf_temp.py")
        with open(temp_conf, "w") as f:
            f.write(content)
        return str(temp_conf)
    
    return None

def build_docs():
    """Build the Sphinx documentation."""
    setup_imghdr_compatibility()
    
    # Change to docs directory
    docs_dir = Path(__file__).parent
    os.chdir(docs_dir)
    
    # Patch the config if needed
    temp_conf = patch_sphinx_config()
    
    # Import sphinx after setting up compatibility
    from sphinx.cmd.build import build_main
    
    # Build arguments
    args = [
        '-b', 'html',          # HTML builder
        '-E',                  # Don't use cached environment
        '.',                   # Source directory
        '_build/html'          # Output directory
    ]
    
    # Use temp conf if created
    if temp_conf:
        # Use temp config
        args = ['-c', os.path.dirname(temp_conf)] + args
    
    print(f"Building documentation with args: {args}")
    return build_main(args)

if __name__ == '__main__':
    sys.exit(build_docs())
