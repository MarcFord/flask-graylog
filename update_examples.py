#!/usr/bin/env python3
"""
Script to update all example files to use correct imports and remove _setup_logging() calls.
"""

import os
import re
from pathlib import Path

# Define the replacements
REPLACEMENTS = [
    # Import replacements
    ("from flask_network_logging import Graylog", "from flask_network_logging import GraylogExtension"),
    ("from flask_network_logging import GCPLog", "from flask_network_logging import GCPLogExtension"),
    ("from flask_network_logging import AWSLog", "from flask_network_logging import AWSLogExtension"),
    ("from flask_network_logging import AzureLog", "from flask_network_logging import AzureLogExtension"),
    ("from flask_network_logging import IBMLog", "from flask_network_logging import IBMLogExtension"),
    ("from flask_network_logging import OCILog", "from flask_network_logging import OCILogExtension"),
    
    # Instance creation replacements
    ("graylog = Graylog(", "graylog = GraylogExtension("),
    ("gcp_log = GCPLog(", "gcp_log = GCPLogExtension("),
    ("aws_log = AWSLog(", "aws_log = AWSLogExtension("),
    ("azure_log = AzureLog(", "azure_log = AzureLogExtension("),
    ("ibm_log = IBMLog(", "ibm_log = IBMLogExtension("),
    ("oci_log = OCILog(", "oci_log = OCILogExtension("),
]

# Pattern to remove _setup_logging() calls
SETUP_LOGGING_PATTERN = re.compile(r'^\s*\w+\._setup_logging\(\)\s*$', re.MULTILINE)

def update_file(file_path):
    """Update a single file with the replacements."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply text replacements
        for old, new in REPLACEMENTS:
            content = content.replace(old, new)
        
        # Remove _setup_logging() calls
        content = SETUP_LOGGING_PATTERN.sub('', content)
        
        # Clean up any double empty lines that might result
        content = re.sub(r'\n\n\n+', '\n\n', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        else:
            print(f"No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Update all Python files in the examples directory."""
    examples_dir = Path("examples")
    
    if not examples_dir.exists():
        print("Examples directory not found!")
        return
    
    updated_count = 0
    total_count = 0
    
    # Find all Python files in examples directory
    for py_file in examples_dir.rglob("*.py"):
        total_count += 1
        if update_file(py_file):
            updated_count += 1
    
    print(f"\nSummary: Updated {updated_count} out of {total_count} Python files.")

if __name__ == "__main__":
    main()
