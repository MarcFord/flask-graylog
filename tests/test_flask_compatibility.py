"""
Tests for Flask version compatibility.

These tests ensure that the package works correctly with different Flask versions,
particularly around environment configuration handling.
"""

from unittest.mock import Mock, patch

import pytest
from flask import Flask

from flask_remote_logging import GraylogExtension
from flask_remote_logging.compat import get_flask_env, set_flask_env


class TestFlaskCompatibility:
    """Test Flask version compatibility features."""

    def test_get_flask_env_with_app_env_attribute(self):
        """Test get_flask_env when app has env attribute (Flask 1.x)."""
        app = Mock()
        app.env = "development"
        app.config = {"ENV": "production"}

        # Should prefer app.env over config['ENV']
        result = get_flask_env(app)
        assert result == "development"

    def test_get_flask_env_without_app_env_attribute(self):
        """Test get_flask_env when app lacks env attribute (Flask 2.x+)."""
        app = Mock()
        # Remove env attribute to simulate Flask 2.x+
        del app.env
        app.config = {"ENV": "production"}

        # Should fall back to config['ENV']
        result = get_flask_env(app)
        assert result == "production"

    def test_get_flask_env_no_config(self):
        """Test get_flask_env with missing config."""
        app = Mock()
        del app.env
        app.config = {}

        # Should return default 'production'
        result = get_flask_env(app)
        assert result == "production"

    def test_get_flask_env_none_app(self):
        """Test get_flask_env with None app."""
        result = get_flask_env(None)
        assert result == "production"

    def test_set_flask_env_with_app_env_attribute(self):
        """Test set_flask_env when app has env attribute."""
        app = Mock()
        app.env = "development"
        app.config = {}

        set_flask_env(app, "staging")

        # Should set both
        assert app.config["ENV"] == "staging"
        # Mock setattr should have been called
        assert app.env == "staging"

    def test_set_flask_env_without_app_env_attribute(self):
        """Test set_flask_env when app lacks env attribute."""
        app = Mock()
        del app.env
        app.config = {}

        set_flask_env(app, "staging")

        # Should set config['ENV']
        assert app.config["ENV"] == "staging"

    def test_set_flask_env_readonly_env_attribute(self):
        """Test set_flask_env when app.env is read-only."""
        app = Mock()
        app.config = {}

        # Make env attribute raise exception when set
        def raise_attribute_error(*args):
            raise AttributeError("can't set attribute")

        with patch("flask_remote_logging.compat.setattr", side_effect=raise_attribute_error):
            # Should not raise exception, just skip setting app.env
            set_flask_env(app, "staging")

            # Should still set config['ENV']
            assert app.config["ENV"] == "staging"

    def test_graylog_extension_flask_env_compatibility(self, app):
        """Test that GraylogExtension works with Flask env compatibility."""
        # Test with Flask 2.x+ style (config['ENV'])
        app.config["ENV"] = "test"
        app.config["GRAYLOG_ENVIRONMENT"] = "test"

        extension = GraylogExtension()
        extension.init_app(app)

        # Should work without errors
        assert extension.app == app

    def test_graylog_extension_with_simulated_flask_1x(self, app):
        """Test GraylogExtension with simulated Flask 1.x environment."""
        # Simulate Flask 1.x by adding env attribute
        app.env = "test"
        app.config["GRAYLOG_ENVIRONMENT"] = "test"

        extension = GraylogExtension()
        extension.init_app(app)

        # Should work without errors
        assert extension.app == app

    def test_flask_env_helper_method_in_extension(self, app):
        """Test that extension's _get_flask_env method works correctly."""
        app.config["ENV"] = "testing"

        extension = GraylogExtension()
        extension.init_app(app)

        # Test the helper method
        env = extension._get_flask_env()
        assert env == "testing"

    def test_flask_env_with_env_attribute_priority(self, app):
        """Test that app.env takes priority over config['ENV'] when both exist."""
        # Simulate having both (some Flask transition scenarios)
        app.env = "development"
        app.config["ENV"] = "production"

        extension = GraylogExtension()
        extension.init_app(app)

        # Should prefer app.env
        env = extension._get_flask_env()
        assert env == "development"

    def test_compatibility_with_real_flask_app(self):
        """Test with actual Flask app instance."""
        app = Flask(__name__)
        app.config["ENV"] = "testing"
        app.config["GRAYLOG_HOST"] = "localhost"
        app.config["GRAYLOG_PORT"] = 12201

        # Should work with real Flask instance
        extension = GraylogExtension()
        extension.init_app(app)

        env = extension._get_flask_env()
        assert env == "testing"

    def test_flask_minimum_version_requirement(self):
        """Test that our Flask requirement is correct."""
        # This test documents the minimum Flask version we support
        import flask

        # Our minimum requirement is Flask 1.4.4
        # Flask version format is typically "2.3.3" or "1.4.4"
        version_parts = flask.__version__.split(".")
        major = int(version_parts[0])
        minor = int(version_parts[1])
        patch = int(version_parts[2]) if len(version_parts) > 2 else 0

        # Should be >= 1.4.4
        assert (major > 1) or (major == 1 and minor > 4) or (major == 1 and minor == 4 and patch >= 4)

    def test_import_compatibility_functions(self):
        """Test that compatibility functions can be imported from main package."""
        from flask_remote_logging import get_flask_env, set_flask_env

        # Should be callable
        assert callable(get_flask_env)
        assert callable(set_flask_env)
