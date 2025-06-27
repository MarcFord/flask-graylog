"""Tests for the GraylogExtension class."""

import logging
from unittest.mock import Mock, patch

import pytest
from flask import Flask
from pygelf import GelfTcpHandler

from flask_remote_logging import GraylogExtension
from flask_remote_logging.context_filter import FlaskRemoteLoggingContextFilter


class TestGraylogExtension:
    """Test cases for the GraylogExtension class."""

    def test_init_without_app(self):
        """Test initialization without a Flask app."""
        extension = GraylogExtension()

        assert extension.app is None
        assert extension.context_filter is None
        assert extension.log_formatter is None
        assert extension.log_level == logging.INFO
        assert extension.additional_logs is None
        assert extension.get_current_user is None
        assert extension.config == {}

    def test_init_with_app(self, app):
        """Test initialization with a Flask app."""
        extension = GraylogExtension(app=app)

        assert extension.app is app
        assert extension.config is not None
        assert "GRAYLOG_HOST" in extension.config

    def test_init_with_parameters(self, app, mock_get_current_user):
        """Test initialization with custom parameters."""
        custom_filter = Mock(spec=logging.Filter)
        custom_formatter = Mock(spec=logging.Formatter)

        extension = GraylogExtension(
            app=app,
            get_current_user=mock_get_current_user,
            context_filter=custom_filter,
            log_formatter=custom_formatter,
            log_level=logging.DEBUG,
            additional_logs=["test.logger"],
        )

        assert extension.app is app
        assert extension.context_filter is custom_filter
        assert extension.log_formatter is custom_formatter
        assert extension.log_level == logging.DEBUG
        assert extension.additional_logs == ["test.logger"]
        assert extension.get_current_user is mock_get_current_user

    def test_init_app(self, app, mock_get_current_user):
        """Test init_app method."""
        extension = GraylogExtension()
        extension.init_app(app, get_current_user=mock_get_current_user)

        assert extension.app is app
        assert extension.config is not None
        assert isinstance(extension.context_filter, FlaskRemoteLoggingContextFilter)
        assert extension.log_formatter is not None

    def test_init_app_with_existing_filter(self, app):
        """Test init_app with existing context filter."""
        custom_filter = Mock(spec=logging.Filter)
        extension = GraylogExtension(context_filter=custom_filter)
        extension.init_app(app)

        assert extension.context_filter is custom_filter

    def test_init_app_with_custom_formatter(self, app):
        """Test init_app with custom log formatter."""
        custom_formatter = Mock(spec=logging.Formatter)
        extension = GraylogExtension(log_formatter=custom_formatter)
        extension.init_app(app)

        assert extension.log_formatter is custom_formatter

    def test_get_config_from_app(self, app):
        """Test configuration retrieval from Flask app."""
        extension = GraylogExtension(app=app)
        config = extension._get_config_from_app()

        assert config["GRAYLOG_HOST"] == "test-host"
        assert config["GRAYLOG_PORT"] == 12201
        assert config["GRAYLOG_APP_NAME"] == "test-app"
        assert config["GRAYLOG_SERVICE_NAME"] == "test-service"
        assert config["GRAYLOG_ENVIRONMENT"] == "test"
        assert config["GRAYLOG_EXTRA_FIELDS"] is True
        assert config["GRAYLOG_DEBUG"] is True
        assert config["GRAYLOG_LOG_LEVEL"] == logging.INFO

    def test_get_config_from_app_defaults(self):
        """Test configuration with default values."""
        app = Flask(__name__)
        extension = GraylogExtension(app=app)
        config = extension._get_config_from_app()

        assert config["GRAYLOG_HOST"] == "localhost"
        assert config["GRAYLOG_PORT"] == 12201
        assert config["GRAYLOG_APP_NAME"] == app.name
        assert config["GRAYLOG_SERVICE_NAME"] == app.name
        assert config["GRAYLOG_ENVIRONMENT"] == "production"
        assert config["GRAYLOG_EXTRA_FIELDS"] is True
        assert config["GRAYLOG_DEBUG"] is True

    def test_get_config_without_app(self):
        """Test configuration retrieval without Flask app raises error."""
        extension = GraylogExtension()

        with pytest.raises(RuntimeError, match="GraylogExtension must be initialized with a Flask app"):
            extension._get_config_from_app()

    @patch("flask_remote_logging.extension.GelfTcpHandler")
    def test_setup_logging_with_graylog_environment(self, mock_handler_class, app):
        """Test logging setup when environment matches Graylog environment."""
        app.env = "test"  # Matches GRAYLOG_ENVIRONMENT in conftest.py
        mock_handler = Mock()
        mock_handler.level = logging.INFO  # Set proper level attribute
        mock_handler_class.return_value = mock_handler

        extension = GraylogExtension(app=app)

        # Verify GelfTcpHandler was created with correct parameters
        mock_handler_class.assert_called_once_with(
            host="test-host",
            port=12201,
            debug=True,
            _app_name="test-app",
            _service_name="test-service",
            _environment="test",
            include_extra_fields=True,
        )

        # Verify handler was configured
        mock_handler.setLevel.assert_called_once_with(logging.INFO)
        mock_handler.addFilter.assert_called_once()

    def test_setup_logging_with_different_environment(self, app, mock_handler, mock_logger):
        """Test logging setup when environment doesn't match Graylog environment."""
        app.env = "development"  # Different from 'test' in config

        # Mock the logger before creating the extension
        with patch.object(app, "logger", mock_logger):
            extension = GraylogExtension(app=app)
            # Setup happens automatically during init
            mock_logger.addHandler.assert_called()

    def test_setup_logging_without_app(self):
        """Test logging setup without Flask app returns gracefully."""
        extension = GraylogExtension()

        # Should not raise an error, just return without setup
        extension._setup_logging()

        # Verify no setup was done
        assert not extension._logging_setup

    def test_setup_logging_with_additional_logs(self, app, mock_logger):
        """Test logging setup with additional loggers."""
        app.env = "development"
        additional_logs = ["test.logger1", "test.logger2"]

        with patch.object(app, "logger", mock_logger), patch("logging.getLogger") as mock_get_logger:
            # Create mock loggers for additional loggers
            mock_logger1 = Mock()
            mock_logger2 = Mock()

            # Set up side effect to handle multiple calls (Flask also calls getLogger)
            def get_logger_side_effect(name):
                if name == "test.logger1":
                    return mock_logger1
                elif name == "test.logger2":
                    return mock_logger2
                else:
                    # Return a new mock for Flask's internal getLogger calls
                    return Mock()

            mock_get_logger.side_effect = get_logger_side_effect

            # Setup happens automatically during init
            extension = GraylogExtension(app=app, additional_logs=additional_logs)

            # Verify additional loggers were configured
            mock_get_logger.assert_any_call("test.logger1")
            mock_get_logger.assert_any_call("test.logger2")

            mock_logger1.setLevel.assert_called_once_with(logging.INFO)
            mock_logger2.setLevel.assert_called_once_with(logging.INFO)
            mock_logger1.addHandler.assert_called_once()
            mock_logger2.addHandler.assert_called_once()
            mock_logger1.addFilter.assert_called_once()
            mock_logger2.addFilter.assert_called_once()

    def test_setup_logging_without_context_filter(self, app, mock_logger):
        """Test logging setup without context filter."""
        with patch.object(app, "logger", mock_logger):
            extension = GraylogExtension(app=app)
            extension.context_filter = None

            # Reset setup flag to allow manual setup test
            extension._logging_setup = False
            extension._setup_logging()

            # Should still add handler without filter
            mock_logger.addHandler.assert_called()

    def test_integration_with_flask_logging(self, app, client, mock_logger):
        """Test integration with Flask application logging."""
        with patch.object(app, "logger", mock_logger):
            extension = GraylogExtension(app=app)

            # Should have called addHandler during automatic setup
            mock_logger.addHandler.assert_called()

    def test_log_level_from_config(self, app):
        """Test that log level is correctly set from config."""
        app.config["GRAYLOG_LOG_LEVEL"] = logging.DEBUG
        extension = GraylogExtension(app=app)

        assert extension.log_level == logging.DEBUG

    def test_log_level_from_parameter_override(self, app):
        """Test that parameter log level overrides config."""
        app.config["GRAYLOG_LOG_LEVEL"] = logging.DEBUG
        extension = GraylogExtension(app=app, log_level=logging.WARNING)
        extension.init_app(app, log_level=logging.ERROR)

        # The init_app log_level should take precedence
        assert extension.log_level == logging.ERROR
