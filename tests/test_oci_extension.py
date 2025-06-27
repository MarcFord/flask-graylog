"""
Tests for Oracle Cloud Infrastructure (OCI) Logging Extension

This module contains comprehensive tests for the OCILogExtension class,
ensuring proper functionality for OCI Logging integration.
"""

import json
import logging
from unittest.mock import MagicMock, Mock, patch

import pytest
from flask import Flask, g, request

from flask_remote_logging.oci_extension import OCILogExtension, OCILogHandler


class TestOCILogExtension:
    """Test suite for OCILogExtension class."""

    def test_init_without_app(self):
        """Test extension initialization without Flask app."""
        extension = OCILogExtension()

        assert extension.app is None
        assert extension.get_current_user is None
        assert extension.log_level == logging.INFO
        assert extension.additional_logs is None
        assert extension.context_filter is None
        assert extension.log_formatter is None

    def test_init_with_app(self):
        """Test extension initialization with Flask app."""
        app = Flask(__name__)
        app.config.update(
            {
                "OCI_LOG_GROUP_ID": "ocid1.loggroup.oc1...",
                "OCI_LOG_ID": "ocid1.log.oc1...",
                "OCI_ENVIRONMENT": "production",
            }
        )

        with patch("flask_remote_logging.oci_extension.oci"):
            extension = OCILogExtension(app=app)

        assert extension.app == app

    def test_init_with_parameters(self):
        """Test extension initialization with custom parameters."""
        extension = OCILogExtension(log_level=logging.DEBUG, additional_logs=["custom.logger"], enable_middleware=False)

        assert extension.log_level == logging.DEBUG
        assert extension.additional_logs == ["custom.logger"]
        assert extension.enable_middleware is False

    def test_init_app_method(self, app):
        """Test init_app method."""
        app.config.update(
            {
                "OCI_LOG_GROUP_ID": "ocid1.loggroup.oc1...",
                "OCI_LOG_ID": "ocid1.log.oc1...",
                "OCI_ENVIRONMENT": "production",
            }
        )

        extension = OCILogExtension()

        with patch("flask_remote_logging.oci_extension.oci"):
            extension.init_app(app)

        assert extension.app == app
        assert extension.config is not None

    def test_get_config_from_app_without_app(self):
        """Test configuration extraction without Flask app."""
        extension = OCILogExtension()
        extension.app = None

        config = extension._get_config_from_app()

        assert config == {}

    def test_get_config_from_app_with_defaults(self):
        """Test configuration extraction with default values."""
        app = Flask(__name__)
        extension = OCILogExtension()
        extension.app = app

        config = extension._get_config_from_app()

        assert "OCI_CONFIG_FILE" in config
        assert "OCI_PROFILE" in config
        assert "OCI_APP_NAME" in config

    def test_get_config_from_app_with_custom_values(self):
        """Test configuration extraction with custom values."""
        app = Flask(__name__)
        app.config.update(
            {
                "OCI_CONFIG_FILE": "~/.oci/custom_config",
                "OCI_PROFILE": "CUSTOM_PROFILE",
                "OCI_LOG_GROUP_ID": "ocid1.loggroup.oc1...",
                "OCI_LOG_ID": "ocid1.log.oc1...",
                "OCI_APP_NAME": "custom-app",
                "OCI_LOG_LEVEL": "DEBUG",
                "OCI_ENVIRONMENT": "production",
            }
        )

        extension = OCILogExtension()
        extension.app = app

        config = extension._get_config_from_app()

        assert config["OCI_CONFIG_FILE"] == "~/.oci/custom_config"
        assert config["OCI_PROFILE"] == "CUSTOM_PROFILE"
        assert config["OCI_LOG_GROUP_ID"] == "ocid1.loggroup.oc1..."
        assert config["OCI_LOG_ID"] == "ocid1.log.oc1..."
        assert config["OCI_APP_NAME"] == "custom-app"

    def test_setup_logging_without_app(self):
        """Test logging setup without Flask app."""
        extension = OCILogExtension()
        extension.app = None

        # Should not raise any exceptions
        extension._setup_logging()

    @patch("flask_remote_logging.oci_extension.oci")
    def test_setup_logging_with_oci_environment(self, mock_oci, app):
        """Test logging setup with OCI environment."""
        app.config.update(
            {
                "OCI_ENVIRONMENT": "production",
                "OCI_LOG_GROUP_ID": "ocid1.loggroup.oc1...",
                "OCI_LOG_ID": "ocid1.log.oc1...",
            }
        )

        extension = OCILogExtension(app=app)

        # Should complete without exceptions
        assert extension.app == app

    def test_setup_logging_with_development_environment(self, app):
        """Test logging setup with development environment (skipped)."""
        app.config.update({"FLASK_REMOTE_LOGGING_ENVIRONMENT": "development"})

        extension = OCILogExtension(app=app)

        # Should complete without exceptions
        assert extension.app == app

    @patch("flask_remote_logging.oci_extension.oci")
    def test_init_backend_with_oci(self, mock_oci):
        """Test OCI backend initialization with OCI SDK available."""
        app = Flask(__name__)
        app.config.update(
            {
                "OCI_CONFIG_FILE": "~/.oci/config",
                "OCI_PROFILE": "DEFAULT",
                "OCI_LOG_GROUP_ID": "ocid1.loggroup.oc1...",
                "OCI_LOG_ID": "ocid1.log.oc1...",
            }
        )

        extension = OCILogExtension()
        extension.app = app
        extension.config = extension._get_config_from_app()

        mock_config = {"region": "us-ashburn-1"}
        mock_oci.config.from_file.return_value = mock_config
        mock_client = Mock()
        mock_oci.logging.LoggingManagementClient.return_value = mock_client

        extension._init_backend()

        assert extension.logging_client == mock_client
        assert extension.log_group_id == "ocid1.loggroup.oc1..."
        assert extension.log_id == "ocid1.log.oc1..."

    @patch("flask_remote_logging.oci_extension.oci")
    def test_init_backend_without_oci(self, mock_oci):
        """Test OCI backend initialization with OCI SDK errors."""
        app = Flask(__name__)
        extension = OCILogExtension()
        extension.app = app
        extension.config = {"OCI_CONFIG_FILE": "~/.oci/config"}

        mock_oci.config.from_file.side_effect = Exception("Config error")

        extension._init_backend()

        assert extension.logging_client is None

    def test_init_backend_without_oci_sdk(self):
        """Test OCI backend initialization without OCI SDK."""
        app = Flask(__name__)
        extension = OCILogExtension()
        extension.app = app
        extension.config = {}

        with patch("flask_remote_logging.oci_extension.oci", None):
            extension._init_backend()

        assert extension.logging_client is None

    @patch("flask_remote_logging.oci_extension.oci")
    def test_create_log_handler_with_client(self, mock_oci):
        """Test log handler creation with OCI client."""
        extension = OCILogExtension()
        extension.logging_client = Mock()
        extension.log_group_id = "ocid1.loggroup.oc1..."
        extension.log_id = "ocid1.log.oc1..."
        extension.config = {"OCI_APP_NAME": "test-app"}

        with patch("flask_remote_logging.oci_extension.OCILogHandler") as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            handler = extension._create_log_handler()

            assert handler == mock_handler
            mock_handler_class.assert_called_once()

    def test_create_log_handler_without_client(self):
        """Test log handler creation without OCI client (fallback to stream)."""
        extension = OCILogExtension()
        extension.logging_client = None
        extension.log_formatter = logging.Formatter("%(message)s")

        handler = extension._create_log_handler()

        assert isinstance(handler, logging.StreamHandler)

    def test_should_skip_setup_development_environment(self):
        """Test setup skipping in development environment."""
        extension = OCILogExtension()
        extension.config = {"FLASK_REMOTE_LOGGING_ENVIRONMENT": "development"}

        assert extension._should_skip_setup() is True

    def test_should_skip_setup_production_environment(self):
        """Test setup not skipping in production environment."""
        extension = OCILogExtension()
        extension.config = {
            "FLASK_REMOTE_LOGGING_ENVIRONMENT": "production",
            "OCI_LOG_GROUP_ID": "ocid1.loggroup.oc1...",
        }

        assert extension._should_skip_setup() is False

    def test_extension_name(self):
        """Test extension name getter."""
        extension = OCILogExtension()
        assert extension._get_extension_name() == "OCI Logging"

    def test_middleware_config_key(self):
        """Test middleware config key getter."""
        extension = OCILogExtension()
        assert extension._get_middleware_config_key() == "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE"

    def test_skip_reason(self):
        """Test skip reason getter."""
        extension = OCILogExtension()
        extension.config = {"FLASK_REMOTE_LOGGING_ENVIRONMENT": "development"}
        assert "no app configured" in extension._get_skip_reason()


class TestOCILogHandler:
    """Test suite for OCILogHandler class."""

    def test_init(self):
        """Test handler initialization."""
        mock_client = Mock()
        handler = OCILogHandler(
            logging_client=mock_client,
            log_group_id="ocid1.loggroup.oc1...",
            log_id="ocid1.log.oc1...",
            app_name="test-app",
        )

        assert handler.logging_client == mock_client
        assert handler.log_group_id == "ocid1.loggroup.oc1..."
        assert handler.log_id == "ocid1.log.oc1..."
        assert handler.app_name == "test-app"

    def test_init_with_defaults(self):
        """Test handler initialization with default values."""
        mock_client = Mock()
        handler = OCILogHandler(
            logging_client=mock_client, log_group_id="ocid1.loggroup.oc1...", log_id="ocid1.log.oc1..."
        )

        assert handler.app_name == "flask-app"

    def test_init_validation(self):
        """Test handler initialization validation."""
        with pytest.raises(ValueError, match="logging_client is required"):
            OCILogHandler(
                logging_client=None, log_group_id="ocid1.loggroup.oc1...", log_id="ocid1.log.oc1..."  # type: ignore
            )

        with pytest.raises(ValueError, match="log_group_id is required"):
            OCILogHandler(logging_client=Mock(), log_group_id=None, log_id="ocid1.log.oc1...")  # type: ignore

        with pytest.raises(ValueError, match="log_id is required"):
            OCILogHandler(logging_client=Mock(), log_group_id="ocid1.loggroup.oc1...", log_id=None)  # type: ignore

    @patch("flask_remote_logging.oci_extension.oci")
    def test_emit_success(self, mock_oci):
        """Test successful log emission."""
        mock_client = Mock()
        handler = OCILogHandler(
            logging_client=mock_client,
            log_group_id="ocid1.loggroup.oc1...",
            log_id="ocid1.log.oc1...",
            app_name="test-app",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))

        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0, msg="Test message", args=(), exc_info=None
        )

        with patch.object(handler, "_send_to_oci_logging") as mock_send:
            handler.emit(record)
            mock_send.assert_called_once()

    def test_emit_error_response(self):
        """Test log emission with OCI API error."""
        mock_client = Mock()
        handler = OCILogHandler(
            logging_client=mock_client,
            log_group_id="ocid1.loggroup.oc1...",
            log_id="ocid1.log.oc1...",
            app_name="test-app",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))

        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0, msg="Test message", args=(), exc_info=None
        )

        with patch.object(handler, "_send_to_oci_logging", side_effect=Exception("API Error")):
            with patch.object(handler, "handleError") as mock_handle_error:
                handler.emit(record)
                mock_handle_error.assert_called_once_with(record)

    @patch("flask_remote_logging.oci_extension.oci", None)
    def test_send_log_data_without_oci(self):
        """Test sending log data without OCI SDK."""
        handler = OCILogHandler(
            logging_client=Mock(), log_group_id="ocid1.loggroup.oc1...", log_id="ocid1.log.oc1...", app_name="test-app"
        )

        log_entry = {"time": "2023-01-01T00:00:00Z", "data": {"message": "test"}}

        with pytest.raises(RuntimeError, match="OCI SDK is not available"):
            handler._send_to_oci_logging(log_entry)

    @patch("flask_remote_logging.oci_extension.oci")
    def test_send_log_data_success(self, mock_oci):
        """Test successful log data sending."""
        mock_client = Mock()
        handler = OCILogHandler(
            logging_client=mock_client,
            log_group_id="ocid1.loggroup.oc1...",
            log_id="ocid1.log.oc1...",
            app_name="test-app",
        )

        log_entry = {"time": "2023-01-01T00:00:00Z", "data": {"message": "test message", "level": "INFO"}}

        handler._send_to_oci_logging(log_entry)

        mock_client.put_logs.assert_called_once()
        call_args = mock_client.put_logs.call_args
        assert call_args.kwargs["log_id"] == "ocid1.log.oc1..."

    @patch("flask_remote_logging.oci_extension.oci")
    def test_handler_integration(self, mock_oci):
        """Test complete handler integration."""
        app = Flask(__name__)

        with app.app_context():
            mock_client = Mock()
            handler = OCILogHandler(
                logging_client=mock_client,
                log_group_id="ocid1.loggroup.oc1...",
                log_id="ocid1.log.oc1...",
                app_name="test-app",
            )
            handler.setFormatter(logging.Formatter("%(message)s"))

            logger = logging.getLogger("test-logger")
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

            # Test that logging works
            with patch.object(handler, "_send_to_oci_logging") as mock_send:
                logger.info("Test log message")
                mock_send.assert_called_once()
