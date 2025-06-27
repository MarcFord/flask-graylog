"""Tests for the GCPLogExtension class."""

import logging
from unittest.mock import MagicMock, Mock, patch

import pytest
from flask import Flask

from flask_remote_logging import GCPLogExtension
from flask_remote_logging.context_filter import FlaskRemoteLoggingContextFilter


class TestGCPLogExtension:
    """Test cases for the GCPLogExtension class."""

    def test_init_without_app(self):
        """Test initialization without a Flask app."""
        extension = GCPLogExtension()

        assert extension.app is None
        assert extension.context_filter is None
        assert extension.log_formatter is None
        assert extension.log_level == logging.INFO
        assert extension.additional_logs is None
        assert extension.get_current_user is None
        assert extension.config == {}
        assert extension.cloud_logging_client is None

    @patch("flask_remote_logging.gcp_extension.cloud_logging")
    def test_init_with_app(self, mock_cloud_logging, app):
        """Test initialization with a Flask app."""
        # Mock the Cloud Logging client
        mock_client = MagicMock()
        mock_cloud_logging.Client.return_value = mock_client

        extension = GCPLogExtension(app=app)

        assert extension.app is app
        assert extension.config is not None
        assert "GCP_PROJECT_ID" in extension.config

    def test_init_with_parameters(self, app, mock_get_current_user):
        """Test initialization with custom parameters."""
        custom_filter = Mock(spec=logging.Filter)
        custom_formatter = Mock(spec=logging.Formatter)

        with patch("flask_remote_logging.gcp_extension.cloud_logging"):
            extension = GCPLogExtension(
                app=app,
                get_current_user=mock_get_current_user,
                context_filter=custom_filter,
                log_formatter=custom_formatter,
                log_level=logging.DEBUG,
                additional_logs=["test.logger"],
            )

            assert extension.app is app
            assert extension.get_current_user is mock_get_current_user
            assert extension.context_filter is custom_filter
            assert extension.log_formatter is custom_formatter
            assert extension.log_level == logging.DEBUG
            assert extension.additional_logs == ["test.logger"]

    @patch("flask_remote_logging.gcp_extension.cloud_logging")
    def test_init_app_method(self, mock_cloud_logging, app):
        """Test the init_app method."""
        mock_client = MagicMock()
        mock_cloud_logging.Client.return_value = mock_client

        extension = GCPLogExtension()
        extension.init_app(app)

        assert extension.app is app
        assert extension.config is not None

    def test_get_config_from_app_without_app(self):
        """Test _get_config_from_app raises error without app."""
        extension = GCPLogExtension()

        with pytest.raises(RuntimeError, match="GCPLogExtension must be initialized with a Flask app"):
            extension._get_config_from_app()

    @patch("flask_remote_logging.gcp_extension.cloud_logging")
    def test_get_config_from_app_with_defaults(self, mock_cloud_logging, app):
        """Test _get_config_from_app with default values."""
        mock_client = MagicMock()
        mock_cloud_logging.Client.return_value = mock_client

        extension = GCPLogExtension(app=app)
        config = extension._get_config_from_app()

        expected_config = {
            "GCP_PROJECT_ID": None,
            "GCP_CREDENTIALS_PATH": None,
            "GCP_LOG_NAME": "flask-app",
            "GCP_LOG_LEVEL": logging.INFO,
            "GCP_APP_NAME": "test_app",  # From the test app fixture
            "GCP_SERVICE_NAME": "test_app",
            "GCP_ENVIRONMENT": "production",
            "FLASK_REMOTE_LOGGING_ENVIRONMENT": "production",  # New standardized key
            "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE": None,
        }

        assert config == expected_config

    @patch("flask_remote_logging.gcp_extension.cloud_logging")
    def test_get_config_from_app_with_custom_values(self, mock_cloud_logging, app):
        """Test _get_config_from_app with custom configuration values."""
        app.config.update(
            {
                "GCP_PROJECT_ID": "my-project",
                "GCP_CREDENTIALS_PATH": "/path/to/credentials.json",
                "GCP_LOG_NAME": "custom-log",
                "GCP_LOG_LEVEL": logging.DEBUG,
                "GCP_APP_NAME": "custom-app",
                "GCP_SERVICE_NAME": "custom-service",
                "GCP_ENVIRONMENT": "staging",
            }
        )

        mock_client = MagicMock()
        mock_cloud_logging.Client.return_value = mock_client

        extension = GCPLogExtension(app=app)
        config = extension._get_config_from_app()

        expected_config = {
            "GCP_PROJECT_ID": "my-project",
            "GCP_CREDENTIALS_PATH": "/path/to/credentials.json",
            "GCP_LOG_NAME": "custom-log",
            "GCP_LOG_LEVEL": logging.DEBUG,
            "GCP_APP_NAME": "custom-app",
            "GCP_SERVICE_NAME": "custom-service",
            "GCP_ENVIRONMENT": "staging",
            "FLASK_REMOTE_LOGGING_ENVIRONMENT": "staging",  # New standardized key
            "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE": None,
        }

        assert config == expected_config

    def test_setup_logging_without_app(self):
        """Test _setup_logging handles no app gracefully."""
        extension = GCPLogExtension()

        # Should not raise an error, just return early
        extension._setup_logging()
        # Verify that logging setup was not performed
        assert not extension._logging_setup

    @patch("flask_remote_logging.gcp_extension.CloudLoggingHandler")
    @patch("flask_remote_logging.gcp_extension.cloud_logging")
    def test_setup_logging_with_gcp_environment(self, mock_cloud_logging, mock_handler_class, app):
        """Test _setup_logging with GCP environment enabled."""
        # Configure app for production environment matching GCP_ENVIRONMENT
        app.env = "production"
        app.config["GCP_ENVIRONMENT"] = "production"
        app.config["GCP_PROJECT_ID"] = "test-project"

        mock_client = MagicMock()
        mock_cloud_logging.Client.return_value = mock_client
        mock_handler = MagicMock()
        mock_handler.level = logging.INFO  # Set proper level for handler
        mock_handler_class.return_value = mock_handler

        extension = GCPLogExtension()
        extension.init_app(app)
        extension._setup_logging()

        # Verify Cloud Logging client was created
        mock_cloud_logging.Client.assert_called_once_with(project="test-project", credentials=None)

        # Verify handler was created with correct parameters
        mock_handler_class.assert_called_once_with(
            mock_client,
            name="flask-app",
            labels={
                "service_name": "test_app",
                "app_name": "test_app",
                "environment": "production",
            },
        )

        # Verify handler was added to app logger
        assert mock_handler in app.logger.handlers

    @patch("flask_remote_logging.gcp_extension.cloud_logging")
    def test_setup_logging_with_development_environment(self, mock_cloud_logging, app):
        """Test _setup_logging with development environment (uses StreamHandler)."""
        # Configure app for development environment
        app.env = "development"
        app.config["GCP_ENVIRONMENT"] = "production"

        mock_client = MagicMock()
        mock_cloud_logging.Client.return_value = mock_client

        extension = GCPLogExtension()
        extension.init_app(app)
        extension._setup_logging()

        # Verify that a StreamHandler was added instead of CloudLoggingHandler
        stream_handlers = [h for h in app.logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(stream_handlers) > 0

    @patch("flask_remote_logging.gcp_extension.CloudLoggingHandler")
    @patch("flask_remote_logging.gcp_extension.cloud_logging")
    def test_setup_logging_with_gcp_failure_fallback(self, mock_cloud_logging, mock_handler_class, app, capfd):
        """Test _setup_logging falls back to StreamHandler when GCP setup fails."""
        # Configure app for production environment
        app.env = "production"
        app.config["GCP_ENVIRONMENT"] = "production"
        app.config["GCP_PROJECT_ID"] = "test-project"  # Need this for _init_backend to run

        # Make Cloud Logging client creation fail
        mock_cloud_logging.Client.side_effect = Exception("GCP authentication failed")

        extension = GCPLogExtension()
        extension.init_app(app)
        extension._setup_logging()

        # Verify that a StreamHandler was added as fallback
        stream_handlers = [h for h in app.logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(stream_handlers) > 0

        # Verify warning was printed
        captured = capfd.readouterr()
        assert "Warning: Failed to setup Google Cloud Logging: GCP authentication failed" in captured.out

    @patch("flask_remote_logging.gcp_extension.cloud_logging")
    def test_setup_logging_with_context_filter(self, mock_cloud_logging, app):
        """Test _setup_logging with context filter."""
        mock_client = MagicMock()
        mock_cloud_logging.Client.return_value = mock_client

        mock_filter = Mock(spec=logging.Filter)

        extension = GCPLogExtension(app=app, context_filter=mock_filter)
        extension._setup_logging()

        # Find the added handler
        added_handlers = [h for h in app.logger.handlers if hasattr(h, "filters")]
        assert len(added_handlers) > 0

        # Check that the filter was added to at least one handler
        filter_added = any(mock_filter in handler.filters for handler in added_handlers)
        assert filter_added

    @patch("flask_remote_logging.gcp_extension.cloud_logging")
    def test_setup_logging_with_additional_logs(self, mock_cloud_logging, app):
        """Test _setup_logging with additional loggers."""
        mock_client = MagicMock()
        mock_cloud_logging.Client.return_value = mock_client

        additional_logs = ["test.logger1", "test.logger2"]

        extension = GCPLogExtension(app=app, additional_logs=additional_logs)
        extension._setup_logging()

        # Check that additional loggers were configured
        for log_name in additional_logs:
            logger = logging.getLogger(log_name)
            assert logger.level == extension.log_level
            assert len(logger.handlers) > 0

    @patch("flask_remote_logging.gcp_extension.cloud_logging")
    def test_context_filter_creation(self, mock_cloud_logging, app):
        """Test that FlaskRemoteLoggingContextFilter is created by default."""
        mock_client = MagicMock()
        mock_cloud_logging.Client.return_value = mock_client

        extension = GCPLogExtension(app=app)

        assert extension.context_filter is not None
        assert isinstance(extension.context_filter, FlaskRemoteLoggingContextFilter)

    @patch("flask_remote_logging.gcp_extension.cloud_logging")
    def test_log_formatter_creation(self, mock_cloud_logging, app):
        """Test that log formatter is created by default."""
        mock_client = MagicMock()
        mock_cloud_logging.Client.return_value = mock_client

        extension = GCPLogExtension(app=app)

        assert extension.log_formatter is not None
        assert isinstance(extension.log_formatter, logging.Formatter)

    @patch("flask_remote_logging.gcp_extension.cloud_logging")
    def test_log_level_parameter_override(self, mock_cloud_logging, app):
        """Test that log_level parameter overrides config."""
        app.config["GCP_LOG_LEVEL"] = logging.ERROR

        mock_client = MagicMock()
        mock_cloud_logging.Client.return_value = mock_client

        # Test that explicit parameter overrides config
        extension = GCPLogExtension(app=app, log_level=logging.DEBUG)
        assert extension.log_level == logging.DEBUG

        # Test that default uses config value
        extension2 = GCPLogExtension(app=app)
        assert extension2.log_level == logging.ERROR


@pytest.fixture
def mock_get_current_user():
    """Mock get_current_user function for testing."""
    return Mock(return_value={"id": "123", "username": "testuser"})


@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask("test_app")
    app.config["TESTING"] = True
    return app
