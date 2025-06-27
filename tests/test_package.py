"""Tests for the flask_remote_logging package module."""

import pytest

import flask_remote_logging


class TestPackageModule:
    """Test cases for the package module."""

    def test_version_attribute_exists(self):
        """Test that __version__ attribute exists."""
        assert hasattr(flask_remote_logging, "__version__")
        assert isinstance(flask_remote_logging.__version__, str)

    def test_version_format(self):
        """Test that version follows semantic versioning format."""
        version = flask_remote_logging.__version__

        # Should be either a development version or proper semver
        assert version == "0.0.1-dev" or len(version.split(".")) >= 2  # At least major.minor

    def test_imports_available(self):
        """Test that main classes can be imported from package."""
        from flask_remote_logging import (
            AWSLog,
            AWSLogExtension,
            AzureLog,
            AzureLogExtension,
            GCPLog,
            GCPLogExtension,
            Graylog,
            GraylogExtension,
            IBMLog,
            IBMLogExtension,
            OCILog,
            OCILogExtension,
        )
        from flask_remote_logging.context_filter import FlaskRemoteLoggingContextFilter

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
        assert FlaskRemoteLoggingContextFilter is not None

        # Test aliases work correctly
        assert Graylog == GraylogExtension
        assert GCPLog == GCPLogExtension
        assert AWSLog == AWSLogExtension
        assert AzureLog == AzureLogExtension
        assert IBMLog == IBMLogExtension
        assert OCILog == OCILogExtension

    def test_package_docstring(self):
        """Test that package has proper docstring."""
        assert flask_remote_logging.__doc__ is not None
        assert "Flask Remote Logging" in flask_remote_logging.__doc__
        assert "Flask extension" in flask_remote_logging.__doc__
        assert "remote logging" in flask_remote_logging.__doc__
