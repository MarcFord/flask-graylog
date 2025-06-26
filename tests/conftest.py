"""Fixtures and utilities for testing flask-graylog."""

import logging
from unittest.mock import Mock

import pytest
from flask import Flask


@pytest.fixture
def app():
    """Create a test Flask application."""
    app = Flask(__name__)
    app.config.update(
        {
            "TESTING": True,
            "GRAYLOG_HOST": "test-host",
            "GRAYLOG_PORT": 12201,
            "GRAYLOG_APP_NAME": "test-app",
            "GRAYLOG_SERVICE_NAME": "test-service",
            "GRAYLOG_ENVIRONMENT": "test",
            "GRAYLOG_EXTRA_FIELDS": True,
            "GRAYLOG_DEBUG": True,
            "GRAYLOG_LOG_LEVEL": logging.INFO,
        }
    )

    # Set env explicitly to avoid Flask version compatibility issues
    if hasattr(app, "env"):
        app.env = "test"  # Match GRAYLOG_ENVIRONMENT
    else:
        # For older Flask versions, set ENV in config
        app.config["ENV"] = "test"

    @app.route("/test")
    def test_route():
        app.logger.info("Test log message")
        return "Test response"

    @app.route("/error")
    def error_route():
        app.logger.error("Test error message")
        raise Exception("Test exception")

    # Clear any problematic handlers after routes are defined
    # This avoids triggering logger creation with potential mock handlers
    try:
        clear_logger_handlers_safely(app.logger)
    except (TypeError, AttributeError):
        # If there are issues with existing handlers, create a fresh logger
        # Reset the logger to a clean state
        app._logger = None

    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def log_record():
    """Create a test log record."""
    return logging.LogRecord(
        name="test", level=logging.INFO, pathname="/test/path.py", lineno=42, msg="Test message", args=(), exc_info=None
    )


@pytest.fixture
def mock_user():
    """Create a mock user object."""
    user = Mock()
    user.id = "123"
    user.uuid = "test-uuid-123"
    user.username = "testuser"
    user.email = "test@example.com"
    return user


@pytest.fixture
def mock_user_dict():
    """Create a mock user dictionary."""
    return {"id": "456", "uuid": "test-uuid-456", "username": "testuser2", "email": "test2@example.com"}


@pytest.fixture
def mock_get_current_user(mock_user):
    """Create a mock get_current_user function."""
    return lambda: mock_user


@pytest.fixture
def mock_get_current_user_dict(mock_user_dict):
    """Create a mock get_current_user function that returns a dict."""
    return lambda: mock_user_dict


@pytest.fixture
def request_headers():
    """Common request headers for testing."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Forwarded-For": "192.168.1.100",
        "X-Request-ID": "test-request-id-123",
    }


@pytest.fixture
def mock_handler():
    """Create a mock handler with proper level attribute."""
    handler = Mock()
    handler.level = logging.INFO
    handler.setLevel = Mock()
    handler.addFilter = Mock()
    handler.setFormatter = Mock()
    return handler


@pytest.fixture
def mock_logger():
    """Create a mock logger with proper handlers."""
    logger = Mock()
    logger.handlers = []
    logger.addHandler = Mock()
    logger.setLevel = Mock()
    logger.level = logging.INFO
    return logger


@pytest.fixture(autouse=True)
def isolate_flask_logger():
    """Fixture to isolate Flask loggers between tests."""
    import logging
    from unittest.mock import Mock

    # Store original loggers
    original_loggers = {}

    yield

    # Clean up any mock handlers that might interfere with subsequent tests
    for name, logger in logging.Logger.manager.loggerDict.items():
        if hasattr(logger, "handlers") and isinstance(logger, logging.Logger):
            # Remove any mock handlers
            handlers_to_remove = []
            for handler in logger.handlers[:]:
                if isinstance(handler, Mock):
                    handlers_to_remove.append(handler)

            for handler in handlers_to_remove:
                logger.removeHandler(handler)


def clear_logger_handlers_safely(logger):
    """Safely clear logger handlers, avoiding Mock objects."""
    import logging
    from unittest.mock import Mock

    # Only clear handlers that are real logging handlers, not mocks
    handlers_to_remove = []
    for handler in logger.handlers[:]:  # Copy list to avoid modification during iteration
        if not isinstance(handler, Mock) and isinstance(handler, logging.Handler):
            handlers_to_remove.append(handler)

    for handler in handlers_to_remove:
        logger.removeHandler(handler)
