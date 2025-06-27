"""
Tests for IBM Cloud Logs Extension
"""

import json
import logging
from unittest.mock import MagicMock, Mock, patch

import pytest
from flask import Flask

from flask_remote_logging.ibm_extension import IBMCloudLogHandler, IBMLogExtension


class TestIBMLogExtension:
    """Test cases for IBMLogExtension."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app = Flask(__name__)
        self.app.config.update(
            {
                "IBM_INGESTION_KEY": "test-key",
                "IBM_HOSTNAME": "test-host",
                "IBM_APP_NAME": "test-app",
                "IBM_ENV": "test",
                "IBM_LOG_LEVEL": "INFO",
                "IBM_ENVIRONMENT": "ibm",
            }
        )

    def test_init_without_app(self):
        """Test extension initialization without Flask app."""
        extension = IBMLogExtension()
        assert extension.app is None
        assert extension.config == {}

    def test_init_with_app(self):
        """Test extension initialization with Flask app."""
        extension = IBMLogExtension(self.app)
        assert extension.app == self.app
        assert extension.config["IBM_INGESTION_KEY"] == "test-key"

    def test_init_app(self):
        """Test init_app method."""
        extension = IBMLogExtension()
        extension.init_app(self.app)
        assert extension.app == self.app
        assert extension.config["IBM_INGESTION_KEY"] == "test-key"

    def test_get_config_from_app(self):
        """Test configuration extraction from Flask app."""
        extension = IBMLogExtension(self.app)
        config = extension._get_config_from_app()

        assert config["IBM_INGESTION_KEY"] == "test-key"
        assert config["IBM_HOSTNAME"] == "test-host"
        assert config["IBM_APP_NAME"] == "test-app"

    def test_get_config_without_app(self):
        """Test configuration extraction without Flask app."""
        extension = IBMLogExtension()
        config = extension._get_config_from_app()
        assert config == {}

    @patch("flask_remote_logging.ibm_extension.requests", None)
    @patch("flask_remote_logging.ibm_extension.requests", None)
    def test_init_ibm_config_without_requests(self):
        """Test IBM config initialization without requests library."""
        extension = IBMLogExtension(self.app)
        extension.ingestion_key = "test-key"  # Set a key so handler creation is attempted

        # The error should occur when creating the handler
        with pytest.raises(RuntimeError) as exc_info:
            IBMCloudLogHandler(ingestion_key="test-key")

        assert "requests library is required" in str(exc_info.value)

    def test_init_ibm_config_missing_key(self):
        """Test IBM config initialization with missing ingestion key."""
        self.app.config["IBM_INGESTION_KEY"] = None
        extension = IBMLogExtension(self.app)

        with patch("flask_remote_logging.ibm_extension.requests"):
            extension._init_ibm_config()
            assert extension.ingestion_key is None

    @patch("flask_remote_logging.ibm_extension.requests")
    def test_setup_logging(self, mock_requests):
        """Test logging setup."""
        with patch.object(IBMLogExtension, "_create_log_handler") as mock_create_handler:
            mock_handler = Mock()
            mock_handler.level = logging.INFO  # Set proper level attribute
            mock_create_handler.return_value = mock_handler
            extension = IBMLogExtension(self.app)
            # Setup happens automatically during init
            mock_create_handler.assert_called()

    @patch("flask_remote_logging.ibm_extension.requests")
    def test_setup_logging_development_env(self, mock_requests):
        """Test logging setup skips in development environment."""
        self.app.config["IBM_ENVIRONMENT"] = "development"
        self.app.config["IBM_INGESTION_KEY"] = None

        extension = IBMLogExtension(self.app)

        with patch.object(extension, "_create_log_handler") as mock_create_handler:
            mock_handler = Mock()
            mock_handler.level = logging.INFO  # Set proper level attribute
            mock_create_handler.return_value = mock_handler
            extension._setup_logging()
            mock_create_handler.assert_not_called()  # Should be skipped due to environment

    @patch("flask_remote_logging.ibm_extension.requests")
    def test_configure_logger_with_handler(self, mock_requests):
        """Test logger configuration with IBM handler."""
        extension = IBMLogExtension(self.app)
        logger = Mock()

        with patch.object(extension, "ingestion_key", "test-key"):
            extension._configure_logger(logger, logging.INFO)

            logger.setLevel.assert_called_with(logging.INFO)
            logger.addHandler.assert_called()

    @patch("flask_remote_logging.ibm_extension.requests")
    def test_configure_logger_no_key(self, mock_requests):
        """Test logger configuration without ingestion key."""
        extension = IBMLogExtension(self.app)
        extension.ingestion_key = None
        logger = Mock()

        extension._configure_logger(logger, logging.INFO)

        logger.setLevel.assert_called_with(logging.INFO)
        # Should only add stream handler, not IBM handler
        assert logger.addHandler.call_count >= 1


class TestIBMCloudLogHandler:
    """Test cases for IBMCloudLogHandler."""

    def setup_method(self):
        """Set up test fixtures."""
        self.handler = IBMCloudLogHandler(ingestion_key="test-key", hostname="test-host", app_name="test-app")

    def test_init(self):
        """Test handler initialization."""
        assert self.handler.ingestion_key == "test-key"
        assert self.handler.hostname == "test-host"
        assert self.handler.app_name == "test-app"

    def test_init_with_defaults(self):
        """Test handler initialization with default values."""
        handler = IBMCloudLogHandler("test-key")
        assert handler.ingestion_key == "test-key"
        assert handler.app_name == "flask-app"
        assert handler.env == "development"

    def test_map_log_level(self):
        """Test log level mapping."""
        assert self.handler._map_log_level("DEBUG") == "Debug"
        assert self.handler._map_log_level("INFO") == "Info"
        assert self.handler._map_log_level("WARNING") == "Warn"
        assert self.handler._map_log_level("ERROR") == "Error"
        assert self.handler._map_log_level("CRITICAL") == "Fatal"
        assert self.handler._map_log_level("UNKNOWN") == "Info"

    @patch("flask_remote_logging.ibm_extension.requests")
    def test_emit_success(self, mock_requests):
        """Test successful log emission."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        # Create a log record
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py", lineno=10, msg="test message", args=(), exc_info=None
        )
        record.created = 1234567890.123

        self.handler.emit(record)

        # Verify the request was made
        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args

        # Check authentication
        assert call_args[1]["auth"] == ("test-key", "")

        # Check payload structure
        payload = call_args[1]["json"]
        assert "lines" in payload
        assert len(payload["lines"]) == 1

        log_line = payload["lines"][0]
        assert log_line["app"] == "test-app"
        assert log_line["level"] == "Info"
        assert "test message" in log_line["line"]

    @patch("flask_remote_logging.ibm_extension.requests")
    def test_emit_with_extra_fields(self, mock_requests):
        """Test log emission with extra fields."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        # Create a log record with extra fields
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py", lineno=10, msg="test message", args=(), exc_info=None
        )
        record.created = 1234567890.123
        record.custom_field = "custom_value"
        record.user_id = 123

        self.handler.emit(record)

        # Check that extra fields are in metadata
        call_args = mock_requests.post.call_args
        payload = call_args[1]["json"]
        log_line = payload["lines"][0]

        assert "meta" in log_line
        assert log_line["meta"]["custom_field"] == "custom_value"
        assert log_line["meta"]["user_id"] == 123

    @patch("flask_remote_logging.ibm_extension.requests")
    def test_emit_error_response(self, mock_requests):
        """Test log emission with error response."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_requests.post.return_value = mock_response

        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py", lineno=10, msg="test message", args=(), exc_info=None
        )
        record.created = 1234567890.123

        # Should not raise exception, but call handleError
        with patch.object(self.handler, "handleError") as mock_handle_error:
            self.handler.emit(record)
            mock_handle_error.assert_called_once()

    @patch("flask_remote_logging.ibm_extension.requests", None)
    def test_send_log_data_without_requests(self):
        """Test sending log data without requests library."""
        with pytest.raises(ImportError) as exc_info:
            self.handler._send_log_data({"lines": []})

        assert "requests library is required" in str(exc_info.value)

    @patch("flask_remote_logging.ibm_extension.requests")
    def test_send_log_data_success(self, mock_requests):
        """Test successful log data sending."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        payload = {"lines": [{"line": "test", "app": "test-app"}]}
        self.handler._send_log_data(payload)

        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args

        # Check URL and auth
        assert call_args[0][0] == "https://logs.us-south.logging.cloud.ibm.com/logs/ingest"
        assert call_args[1]["auth"] == ("test-key", "")
        assert call_args[1]["json"] == payload

    @patch("flask_remote_logging.ibm_extension.requests")
    def test_send_log_data_with_optional_params(self, mock_requests):
        """Test log data sending with optional parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response

        handler = IBMCloudLogHandler(
            ingestion_key="test-key",
            hostname="test-host",
            ip="192.168.1.1",
            mac="AA:BB:CC:DD:EE:FF",
            tags=["tag1", "tag2"],
        )

        payload = {"lines": []}
        handler._send_log_data(payload)

        call_args = mock_requests.post.call_args
        params = call_args[1]["params"]

        assert params["hostname"] == "test-host"
        assert params["ip"] == "192.168.1.1"
        assert params["mac"] == "AA:BB:CC:DD:EE:FF"
        assert params["tags"] == "tag1,tag2"

    def test_handler_integration(self):
        """Test handler integration with Python logging."""
        # This tests that the handler can be used with Python's logging system
        logger = logging.getLogger("test_ibm")
        logger.addHandler(self.handler)
        logger.setLevel(logging.INFO)

        with patch.object(self.handler, "emit") as mock_emit:
            logger.info("Test message")
            mock_emit.assert_called_once()
