"""Integration tests for flask-graylog package."""

import logging
from unittest.mock import Mock, patch

import pytest
from flask import Flask, g

from flask_remote_logging import GraylogExtension
from flask_remote_logging.context_filter import FlaskRemoteLoggingContextFilter


class TestIntegration:
    """Integration tests for the complete flask-graylog package."""

    def test_complete_integration(self, app, client, mock_get_current_user):
        """Test complete integration with Flask application."""
        # Setup extension
        extension = GraylogExtension(app=app, get_current_user=mock_get_current_user, log_level=logging.INFO)

        # Test logging with request context
        with patch.object(app.logger, "info") as mock_log:
            response = client.get(
                "/test?param1=value1",
                headers={
                    "X-Request-ID": "integration-test-id",
                    "User-Agent": "Test Browser/1.0",
                    "X-Forwarded-For": "192.168.1.100",
                },
            )

            assert response.status_code == 200
            # Should have been called twice: once for the test route, once for middleware
            assert mock_log.call_count == 2
            # Check the first call was from the test route
            mock_log.assert_any_call("Test log message")
            # Check the second call was from middleware (contains request finishing info)
            middleware_call = mock_log.call_args_list[1]
            assert "Finishing request" in middleware_call[0][0]

    def test_logging_without_request_context(self, app, mock_get_current_user):
        """Test logging outside of request context."""
        extension = GraylogExtension(app=app, get_current_user=mock_get_current_user)
        extension._setup_logging()

        # Log outside request context
        with patch.object(app.logger, "info") as mock_log:
            app.logger.info("Test message outside request")
            mock_log.assert_called_once()

    def test_error_logging_integration(self, app, client):
        """Test error logging integration."""
        extension = GraylogExtension(app=app)
        extension._setup_logging()

        with patch.object(app.logger, "error") as mock_log:
            try:
                client.get("/error")
            except Exception:
                pass  # Expected exception

            mock_log.assert_called_once()

    def test_multiple_loggers_integration(self, app):
        """Test integration with multiple loggers."""
        additional_loggers = ["test.logger1", "test.logger2"]

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger1 = Mock()
            mock_logger2 = Mock()
            mock_get_logger.side_effect = [mock_logger1, mock_logger2]

            # Setup happens automatically during init
            extension = GraylogExtension(app=app, additional_logs=additional_loggers)

            # Verify both additional loggers were configured
            assert mock_get_logger.call_count == 2
            mock_logger1.addHandler.assert_called_once()
            mock_logger2.addHandler.assert_called_once()

    def test_graylog_handler_integration(self, app):
        """Test integration with GelfTcpHandler when environment matches."""
        app.env = "test"  # Matches config

        with patch("flask_remote_logging.extension.GelfTcpHandler") as mock_handler_class:
            mock_handler = Mock()
            mock_handler.level = logging.INFO  # Set proper level attribute
            mock_handler_class.return_value = mock_handler

            extension = GraylogExtension(app=app)

            # Verify GelfTcpHandler was used
            mock_handler_class.assert_called_once()
            mock_handler.setLevel.assert_called_once()

    def test_stream_handler_integration(self, app):
        """Test integration with StreamHandler when environment doesn't match."""
        # Set the app environment and the Graylog environment to different values
        app.env = "development"  # This will be used as the current environment
        app.config["GRAYLOG_ENVIRONMENT"] = "production"  # Override the config

        original_handlers = len(app.logger.handlers)

        # Create extension - setup happens automatically during init
        extension = GraylogExtension(app=app)

        # Should add a StreamHandler since app.env ('development') doesn't match GRAYLOG_ENVIRONMENT ('production')
        assert len(app.logger.handlers) == original_handlers + 1
        new_handler = app.logger.handlers[-1]
        assert isinstance(new_handler, logging.StreamHandler)

    def test_user_context_integration(self, app, client, mock_get_current_user):
        """Test user context integration in logs."""
        extension = GraylogExtension(app=app, get_current_user=mock_get_current_user)
        extension._setup_logging()

        # Create a custom log handler to capture log records
        captured_records = []

        class CapturingHandler(logging.Handler):
            def emit(self, record):
                captured_records.append(record)

        capturing_handler = CapturingHandler()
        capturing_handler.setLevel(logging.DEBUG)  # Ensure it captures all levels
        app.logger.addHandler(capturing_handler)

        with app.test_request_context("/test"):
            app.logger.info("Test message with user context")

        # Check that user info was added to log record
        assert len(captured_records) > 0
        record = captured_records[0]
        assert hasattr(record, "id")
        assert hasattr(record, "username")
        assert record.id == "123"
        assert record.username == "testuser"

    def test_request_context_integration(self, app, client):
        """Test request context integration in logs."""
        extension = GraylogExtension(app=app)
        extension._setup_logging()

        captured_records = []

        class CapturingHandler(logging.Handler):
            def emit(self, record):
                captured_records.append(record)

        capturing_handler = CapturingHandler()
        app.logger.addHandler(capturing_handler)

        with app.test_request_context(
            "/test?param1=value1",
            headers={
                "X-Request-ID": "test-req-id",
                "User-Agent": "Test Browser/1.0",
                "X-Forwarded-For": "192.168.1.100",
            },
        ):
            app.logger.info("Test message with request context")

        # Check that request info was added to log record
        assert len(captured_records) > 0
        record = captured_records[0]
        assert hasattr(record, "request_id")
        assert hasattr(record, "client_ip_address")
        assert hasattr(record, "user_agent")
        assert hasattr(record, "url")
        assert record.request_id == "test-req-id"
        assert record.user_agent == "Test Browser/1.0"

    def test_sensitive_data_filtering_integration(self, app):
        """Test that sensitive data is properly filtered in integration."""
        extension = GraylogExtension(app=app)
        extension._setup_logging()

        captured_records = []

        class CapturingHandler(logging.Handler):
            def emit(self, record):
                captured_records.append(record)

        capturing_handler = CapturingHandler()
        app.logger.addHandler(capturing_handler)

        with app.test_request_context("/test?username=testuser&password=secret123"):
            app.logger.info("Test message with sensitive data")

        # Check that sensitive data was filtered
        assert len(captured_records) > 0
        record = captured_records[0]
        assert hasattr(record, "username")
        assert hasattr(record, "password")
        assert record.username == "testuser"
        assert record.password == "*********"  # Masked

    def test_configuration_override_integration(self, app):
        """Test configuration override in integration scenario."""
        # Override some config values
        app.config.update({"GRAYLOG_HOST": "custom-host", "GRAYLOG_PORT": 9999, "GRAYLOG_LOG_LEVEL": logging.DEBUG})

        extension = GraylogExtension(app=app)
        config = extension._get_config_from_app()

        assert config["GRAYLOG_HOST"] == "custom-host"
        assert config["GRAYLOG_PORT"] == 9999
        assert extension.log_level == logging.DEBUG

    def test_no_context_filter_integration(self, app):
        """Test integration without context filter."""
        original_handlers = len(app.logger.handlers)

        # Create extension with context filter disabled
        extension = GraylogExtension(app=app, context_filter=None)

        # Should still add handler even without context filter
        assert len(app.logger.handlers) == original_handlers + 1

    def test_custom_formatter_integration(self, app):
        """Test integration with custom formatter."""
        custom_formatter = logging.Formatter("CUSTOM: %(message)s")
        extension = GraylogExtension(app=app, log_formatter=custom_formatter)

        assert extension.log_formatter is custom_formatter

    def test_extension_reinitialization(self, app, mock_get_current_user):
        """Test that extension can be reinitialized."""
        extension = GraylogExtension()

        # First initialization
        extension.init_app(app)
        first_config = extension.config.copy()

        # Second initialization with different parameters
        extension.init_app(app, get_current_user=mock_get_current_user, log_level=logging.DEBUG)

        assert extension.get_current_user is mock_get_current_user
        assert extension.log_level == logging.DEBUG

    def test_thread_safety_integration(self, app):
        """Test basic thread safety concerns."""
        extension = GraylogExtension(app=app)

        # Multiple filter instances should be independent
        filter1 = FlaskRemoteLoggingContextFilter()
        filter2 = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test1", headers={"X-Request-ID": "req1"}):
            filter1._FlaskRemoteLoggingContextFilter__request = filter1.request
            req_id_1 = filter1.request_id

        with app.test_request_context("/test2", headers={"X-Request-ID": "req2"}):
            filter2._FlaskRemoteLoggingContextFilter__request = filter2.request
            req_id_2 = filter2.request_id

        # Each filter should maintain its own state
        assert req_id_1 == "req1"
        assert req_id_2 == "req2"

    def test_exception_handling_in_logging(self, app):
        """Test that exceptions in logging don't break the application."""
        extension = GraylogExtension(app=app)

        # Mock a problematic get_current_user function
        def problematic_get_user():
            raise Exception("Database connection error")

        extension.get_current_user = problematic_get_user
        extension.context_filter = FlaskRemoteLoggingContextFilter(get_current_user=problematic_get_user)
        extension._setup_logging()

        captured_records = []

        class CapturingHandler(logging.Handler):
            def emit(self, record):
                captured_records.append(record)

        capturing_handler = CapturingHandler()
        app.logger.addHandler(capturing_handler)

        # This shouldn't raise an exception
        with app.test_request_context("/test"):
            app.logger.info("Test message")

        # Should still log the message despite user function error
        assert len(captured_records) > 0
