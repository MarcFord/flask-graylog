"""Tests for the flask_graylog package module."""

import pytest

import flask_graylog


class TestPackageModule:
    """Test cases for the package module."""

    def test_version_attribute_exists(self):
        """Test that __version__ attribute exists."""
        assert hasattr(flask_graylog, "__version__")
        assert isinstance(flask_graylog.__version__, str)

    def test_version_format(self):
        """Test that version follows semantic versioning format."""
        version = flask_graylog.__version__

        # Should be either a development version or proper semver
        assert version == "0.0.1-dev" or len(version.split(".")) >= 2  # At least major.minor

    def test_imports_available(self):
        """Test that main classes can be imported from package."""
        from flask_graylog import GraylogExtension
        from flask_graylog.context_filter import GraylogContextFilter

        assert GraylogExtension is not None
        assert GraylogContextFilter is not None

    def test_package_docstring(self):
        """Test that package has proper docstring."""
        assert flask_graylog.__doc__ is not None
        assert "Flask Graylog" in flask_graylog.__doc__
        assert "Flask extension" in flask_graylog.__doc__
