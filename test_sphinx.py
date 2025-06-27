#!/usr/bin/env python3

import sys
from sphinx.cmd.build import build_main

print("Python version:", sys.version)
print("Running test build with minimal config...")

sys.argv = [
    "sphinx-build",
    "-b", "html",
    "-D", "extensions=myst_parser",
    "-D", "source_suffix=.md=markdown",
    "-C",  # Use no config file
    "docs",
    "docs/_build/html"
]

sys.exit(build_main())
