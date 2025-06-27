#!/bin/bash
# Script to build Flask Network Logging documentation
# This script uses Python 3.9 virtual environment to avoid issues with Python 3.13+

# Name of the virtual environment
VENV_NAME=".venv-py39"
PYTHON_VERSION="python3.9" 
PROJECT_ROOT="/home/mford/Projects/github.com/MarcFord/flask-remote-logging"
DOCS_DIR="${PROJECT_ROOT}/docs"

# Check for Python 3.9
if ! command -v ${PYTHON_VERSION} &> /dev/null; then
    echo "Error: ${PYTHON_VERSION} is required but not found"
    exit 1
fi

# Ensure the virtual environment exists
if [ ! -d "${PROJECT_ROOT}/${VENV_NAME}" ]; then
    echo "Creating virtual environment with ${PYTHON_VERSION}..."
    cd "${PROJECT_ROOT}"
    uv venv -p ${PYTHON_VERSION} ${VENV_NAME}
    source "${PROJECT_ROOT}/${VENV_NAME}/bin/activate"
    uv pip install -e ".[docs]"
else
    echo "Using existing virtual environment..."
    source "${PROJECT_ROOT}/${VENV_NAME}/bin/activate"
fi

# Build the documentation
echo "Building documentation with $(python --version)..."
cd "${DOCS_DIR}"
sphinx-build -b html . _build/html

# Check build status
if [ $? -eq 0 ]; then
    echo ""
    echo "Documentation built successfully!"
    echo "Open the following URL in your browser to view it:"
    echo "file://${DOCS_DIR}/_build/html/index.html"
else
    echo "Documentation build failed."
    exit 1
fi
