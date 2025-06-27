"""Tests for the Azure Monitor Logs extension."""

import json
import logging
from unittest.mock import MagicMock, Mock, patch

import pytest
from flask import Flask

from flask_remote_logging.azure_extension import AzureLogExtension, AzureMonitorHandler
from flask_remote_logging.context_filter import FlaskRemoteLoggingContextFilter


class TestAzureLogExtension:
    """Test cases for the AzureLogExtension class."""

    def test_init_without_app(self):
        """Test extension initialization without Flask app."""
        extension = AzureLogExtension()

        assert extension.app is None
        assert extension.get_current_user is None
        assert extension.log_level == logging.INFO
        assert extension.additional_logs == []
        assert extension.context_filter is None
        assert extension.log_formatter is None
        assert extension.config == {}

    def test_init_with_app(self):
        """Test extension initialization with Flask app."""
        app = Flask(__name__)
        extension = AzureLogExtension(app)

        assert extension.app is app
        assert isinstance(extension.config, dict)

    def test_init_with_parameters(self):
        """Test extension initialization with custom parameters."""
        app = Flask(__name__)
        mock_get_user = Mock()
        custom_filter = Mock()
        custom_formatter = Mock()

        extension = AzureLogExtension(
            app,
            get_current_user=mock_get_user,
            log_level=logging.DEBUG,
            additional_logs=["test.logger"],
            context_filter=custom_filter,
            log_formatter=custom_formatter,
        )

        assert extension.app is app
        assert extension.get_current_user is mock_get_user
        assert extension.log_level == logging.DEBUG
        assert extension.additional_logs == ["test.logger"]
        assert extension.context_filter is custom_filter
        assert extension.log_formatter is custom_formatter

    def test_init_app_method(self):
        """Test init_app method."""
        app = Flask(__name__)
        extension = AzureLogExtension()

        extension.init_app(app)

        assert extension.app is app
        assert isinstance(extension.config, dict)

    def test_get_config_from_app_without_app(self):
        """Test config extraction when no app is set."""
        extension = AzureLogExtension()
        config = extension._get_config_from_app()

        assert config == {}

    def test_get_config_from_app_with_defaults(self):
        """Test config extraction with default values."""
        app = Flask(__name__)
        extension = AzureLogExtension(app)

        config = extension._get_config_from_app()

        assert config["AZURE_LOG_TYPE"] == "FlaskAppLogs"
        assert config["AZURE_LOG_LEVEL"] == "INFO"
        assert config["AZURE_ENVIRONMENT"] == "development"
        assert config["AZURE_TIMEOUT"] == "30"

    def test_get_config_from_app_with_custom_values(self):
        """Test config extraction with custom values."""
        app = Flask(__name__)
        app.config.update(
            {
                "AZURE_WORKSPACE_ID": "test-workspace-id",
                "AZURE_WORKSPACE_KEY": "test-workspace-key",
                "AZURE_LOG_TYPE": "CustomLogs",
                "AZURE_LOG_LEVEL": "DEBUG",
                "AZURE_ENVIRONMENT": "production",
                "AZURE_TIMEOUT": "60",
            }
        )

        extension = AzureLogExtension(app)
        config = extension._get_config_from_app()

        assert config["AZURE_WORKSPACE_ID"] == "test-workspace-id"
        assert config["AZURE_WORKSPACE_KEY"] == "test-workspace-key"
        assert config["AZURE_LOG_TYPE"] == "CustomLogs"
        assert config["AZURE_LOG_LEVEL"] == "DEBUG"
        assert config["AZURE_ENVIRONMENT"] == "production"
        assert config["AZURE_TIMEOUT"] == "60"

    def test_setup_logging_without_app(self):
        """Test setup logging when no app is configured."""
        extension = AzureLogExtension()
        extension._setup_logging()  # Should not raise an error

    @patch("flask_remote_logging.azure_extension.requests")
    def test_setup_logging_with_azure_environment(self, mock_requests):
        """Test logging setup with Azure environment."""
        app = Flask(__name__)
        app.config.update(
            {
                "AZURE_ENVIRONMENT": "azure",
                "AZURE_WORKSPACE_ID": "test-workspace-id",
                "AZURE_WORKSPACE_KEY": "test-workspace-key",
            }
        )

        extension = AzureLogExtension(app)
        extension._setup_logging()

        # Should have set up logging
        assert extension.context_filter is not None
        assert extension.log_formatter is not None

    def test_setup_logging_with_development_environment(self):
        """Test logging setup skips in development environment."""
        app = Flask(__name__)
        app.config.update({"AZURE_ENVIRONMENT": "development"})

        extension = AzureLogExtension(app)

        # Context filter should be created during init but logging should be skipped
        assert extension.context_filter is not None
        # Verify the extension was properly initialized but skipped actual logging setup
        assert extension._logging_setup is True  # Setup was run but skipped

    @patch("flask_remote_logging.azure_extension.requests")
    def test_init_azure_config_with_credentials(self, mock_requests):
        """Test Azure configuration initialization with credentials."""
        app = Flask(__name__)
        app.config.update(
            {
                "AZURE_WORKSPACE_ID": "test-workspace-id",
                "AZURE_WORKSPACE_KEY": "test-workspace-key",
                "AZURE_LOG_TYPE": "TestLogs",
            }
        )

        extension = AzureLogExtension(app)

        assert extension.workspace_id == "test-workspace-id"
        assert extension.workspace_key == "test-workspace-key"
        assert extension.log_type == "TestLogs"

    @patch("flask_remote_logging.azure_extension.requests")
    def test_init_azure_config_without_credentials(self, mock_requests):
        """Test Azure configuration initialization without credentials."""
        app = Flask(__name__)
        extension = AzureLogExtension(app)

        assert extension.workspace_id is None
        assert extension.workspace_key is None

    def test_init_azure_config_without_requests(self):
        """Test Azure configuration initialization without requests library."""
        with patch("flask_remote_logging.azure_extension.requests", None):
            app = Flask(__name__)
            extension = AzureLogExtension(app)

            # Should handle missing requests gracefully

    @patch("flask_remote_logging.azure_extension.requests")
    def test_setup_logging_with_context_filter(self, mock_requests):
        """Test that FlaskRemoteLoggingContextFilter is created by default."""
        app = Flask(__name__)
        app.config.update(
            {
                "AZURE_ENVIRONMENT": "production",
                "AZURE_WORKSPACE_ID": "test-workspace-id",
                "AZURE_WORKSPACE_KEY": "test-workspace-key",
            }
        )

        extension = AzureLogExtension(app)
        extension._setup_logging()

        assert isinstance(extension.context_filter, FlaskRemoteLoggingContextFilter)

    @patch("flask_remote_logging.azure_extension.requests")
    def test_setup_logging_with_additional_logs(self, mock_requests):
        """Test setup logging with additional loggers."""
        app = Flask(__name__)
        app.config.update(
            {
                "AZURE_ENVIRONMENT": "azure",
                "AZURE_WORKSPACE_ID": "test-workspace-id",
                "AZURE_WORKSPACE_KEY": "test-workspace-key",
            }
        )

        extension = AzureLogExtension(app, additional_logs=["test.logger"])
        extension._setup_logging()

        # Should configure additional loggers
        assert extension.additional_logs is not None
        assert "test.logger" in extension.additional_logs

    @patch("flask_remote_logging.azure_extension.requests")
    def test_context_filter_creation(self, mock_requests):
        """Test that context filter is created correctly."""
        app = Flask(__name__)
        app.config.update(
            {
                "AZURE_ENVIRONMENT": "production",
                "AZURE_WORKSPACE_ID": "test-workspace-id",
                "AZURE_WORKSPACE_KEY": "test-workspace-key",
            }
        )

        extension = AzureLogExtension(app)
        extension._setup_logging()

        assert extension.context_filter is not None
        assert isinstance(extension.context_filter, FlaskRemoteLoggingContextFilter)

    @patch("flask_remote_logging.azure_extension.requests")
    def test_log_formatter_creation(self, mock_requests):
        """Test that log formatter is created correctly."""
        app = Flask(__name__)
        app.config.update(
            {
                "AZURE_ENVIRONMENT": "production",
                "AZURE_WORKSPACE_ID": "test-workspace-id",
                "AZURE_WORKSPACE_KEY": "test-workspace-key",
            }
        )

        extension = AzureLogExtension(app)
        extension._setup_logging()

        assert extension.log_formatter is not None
        assert isinstance(extension.log_formatter, logging.Formatter)

    @patch("flask_remote_logging.azure_extension.requests")
    def test_log_level_parameter_override(self, mock_requests):
        """Test that log level parameter overrides config."""
        app = Flask(__name__)
        app.config.update(
            {
                "AZURE_ENVIRONMENT": "production",
                "AZURE_WORKSPACE_ID": "test-workspace-id",
                "AZURE_WORKSPACE_KEY": "test-workspace-key",
                "AZURE_LOG_LEVEL": "INFO",
            }
        )

        extension = AzureLogExtension(app, log_level=logging.DEBUG)

        assert extension.log_level == logging.DEBUG


class TestAzureMonitorHandler:
    """Test cases for the AzureMonitorHandler class."""

    def test_azure_monitor_handler_init(self):
        """Test Azure Monitor handler initialization."""
        handler = AzureMonitorHandler(
            workspace_id="test-workspace-id", workspace_key="test-workspace-key", log_type="TestLogs"
        )

        assert handler.workspace_id == "test-workspace-id"
        assert handler.workspace_key == "test-workspace-key"
        assert handler.log_type == "TestLogs"
        assert handler.timeout == 30
        assert "test-workspace-id.ods.opinsights.azure.com" in handler.uri

    @patch("flask_remote_logging.azure_extension.requests")
    def test_azure_monitor_handler_emit(self, mock_requests):
        """Test Azure Monitor handler emit method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        handler = AzureMonitorHandler(
            workspace_id="test-workspace-id", workspace_key="test-workspace-key", log_type="TestLogs"
        )

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        # Verify that POST request was made
        mock_requests.post.assert_called_once()

        # Check the call arguments
        call_args = mock_requests.post.call_args
        assert "test-workspace-id.ods.opinsights.azure.com" in call_args[0][0]
        assert call_args[1]["headers"]["Log-Type"] == "TestLogs"

    @patch("flask_remote_logging.azure_extension.requests")
    def test_azure_monitor_handler_emit_with_extra_fields(self, mock_requests):
        """Test Azure Monitor handler emit with extra fields."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        handler = AzureMonitorHandler(
            workspace_id="test-workspace-id", workspace_key="test-workspace-key", log_type="TestLogs"
        )

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Add extra fields
        record.custom_field = "custom_value"
        record.request_id = "test-request-id"

        handler.emit(record)

        # Verify that POST request was made
        mock_requests.post.assert_called_once()

        # Check that extra fields are included in the JSON data
        call_args = mock_requests.post.call_args
        json_data = json.loads(call_args[1]["data"])
        assert json_data[0]["custom_field"] == "custom_value"
        assert json_data[0]["request_id"] == "test-request-id"

    @patch("flask_remote_logging.azure_extension.requests")
    def test_azure_monitor_handler_emit_http_error(self, mock_requests):
        """Test Azure Monitor handler with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_requests.post.return_value = mock_response

        handler = AzureMonitorHandler(
            workspace_id="test-workspace-id", workspace_key="test-workspace-key", log_type="TestLogs"
        )

        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Should handle error gracefully (calls handleError)
        with patch.object(handler, "handleError") as mock_handle_error:
            handler.emit(record)
            mock_handle_error.assert_called_once()

    def test_azure_monitor_handler_emit_without_requests(self):
        """Test Azure Monitor handler without requests library."""
        with patch("flask_remote_logging.azure_extension.requests", None):
            handler = AzureMonitorHandler(
                workspace_id="test-workspace-id", workspace_key="test-workspace-key", log_type="TestLogs"
            )

            record = logging.LogRecord(
                name="test.logger",
                level=logging.INFO,
                pathname="/test/path.py",
                lineno=123,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            # Should handle missing requests gracefully
            with patch.object(handler, "handleError") as mock_handle_error:
                handler.emit(record)
                mock_handle_error.assert_called_once()
