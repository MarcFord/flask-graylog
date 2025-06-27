"""Tests for the flask_network_logging package module."""

import pytest

import flask_network_logging


class TestPackageModule:
    """Test cases for the package module."""

    def test_version_attribute_exists(self):
        """Test that __version__ attribute exists."""
        assert hasattr(flask_network_logging, "__version__")
        assert isinstance(flask_network_logging.__version__, str)

    def test_version_format(self):
        """Test that version follows semantic versioning format."""
        version = flask_network_logging.__version__

        # Should be either a development version or proper semver
        assert version == "0.0.1-dev" or len(version.split(".")) >= 2  # At least major.minor

    def test_imports_available(self):
        """Test that main classes can be imported from package."""
        from flask_network_logging import (
            GraylogExtension, GCPLogExtension, AWSLogExtension, 
            AzureLogExtension, IBMLogExtension, OCILogExtension,
            Graylog, GCPLog, AWSLog, AzureLog, IBMLog, OCILog
        )
        from flask_network_logging.context_filter import GraylogContextFilter

        assert GraylogExtension is not None
        assert GCPLogExtension is not None
        assert AWSLogExtension is not None
        assert AzureLogExtension is not None
        assert IBMLogExtension is not None
        assert OCILogExtension is not None
        assert Graylog is not None
        assert GCPLog is not None
        assert AWSLog is not None
        assert AzureLog is not None
        assert IBMLog is not None
        assert OCILog is not None
        assert GraylogContextFilter is not None
        
        # Test aliases work correctly
        assert Graylog == GraylogExtension
        assert GCPLog == GCPLogExtension
        assert AWSLog == AWSLogExtension
        assert AzureLog == AzureLogExtension
        assert IBMLog == IBMLogExtension
        assert OCILog == OCILogExtension

    def test_package_docstring(self):
        """Test that package has proper docstring."""
        assert flask_network_logging.__doc__ is not None
        assert "Flask Network Logging" in flask_network_logging.__doc__
        assert "Flask extension" in flask_network_logging.__doc__
        assert "remote logging" in flask_network_logging.__doc__
