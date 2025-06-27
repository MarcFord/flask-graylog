"""
Tests for middleware functionality in flask-network-logging.

This module tests the request/response middleware that can be enabled
for all logging extensions.
"""

import json
import time
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask, g, jsonify

from src.flask_remote_logging.middleware import after_request, before_request, setup_middleware


class TestMiddleware:
    """Test cases for middleware functionality."""

    def test_setup_middleware(self):
        """Test that middleware is properly registered with Flask app."""
        app = Flask(__name__)

        # Mock the before_request and after_request decorators
        with patch.object(app, "before_request") as mock_before, patch.object(app, "after_request") as mock_after:

            setup_middleware(app)

            # Verify middleware functions were registered
            mock_before.assert_called_once_with(before_request)
            mock_after.assert_called_once_with(after_request)

    def test_before_request_sets_timing(self):
        """Test that before_request sets timing information in g."""
        app = Flask(__name__)

        with app.test_request_context("/test"):
            before_time = time.time()
            before_request()
            after_time = time.time()

            # Check that timing was set
            assert hasattr(g, "flask_remote_logging")
            assert isinstance(g.flask_remote_logging, float)
            assert before_time <= g.flask_remote_logging <= after_time

    def test_after_request_calculates_duration(self):
        """Test that after_request calculates request duration."""
        app = Flask(__name__)

        with app.test_request_context("/test"):
            # Set up timing like before_request would
            g.flask_remote_logging = time.time() - 0.5  # 500ms ago

            # Create a mock response
            response = MagicMock()
            response.headers = {}
            response.status_code = 200

            with patch.object(app.logger, "info") as mock_logger:
                result = after_request(response)

                # Should return the same response
                assert result == response

                # Should have logged with timing information
                mock_logger.assert_called_once()
                call_args = mock_logger.call_args

                # Check that extra data includes timing
                extra_data = call_args[1]["extra"]
                assert "response" in extra_data
                assert "time_ms" in extra_data["response"]
                assert extra_data["response"]["time_ms"] > 0

    def test_after_request_without_timing(self):
        """Test that after_request handles missing timing gracefully."""
        app = Flask(__name__)

        with app.test_request_context("/test"):
            # Don't set timing in g

            # Create a mock response
            response = MagicMock()
            response.headers = {}
            response.status_code = 200

            with patch.object(app.logger, "info") as mock_logger:
                result = after_request(response)

                # Should return the same response
                assert result == response

                # Should have logged with 0 timing
                mock_logger.assert_called_once()
                call_args = mock_logger.call_args

                # Check that timing defaults to 0
                extra_data = call_args[1]["extra"]
                assert extra_data["response"]["time_ms"] == 0

    def test_after_request_includes_request_data(self):
        """Test that after_request includes comprehensive request data."""
        app = Flask(__name__)

        with app.test_request_context(
            "/api/test?param=value",
            method="POST",
            headers={"User-Agent": "test-agent", "Content-Type": "application/json"},
        ):
            g.flask_remote_logging = time.time()

            # Create a mock response
            response = MagicMock()
            response.headers = [("Content-Type", "application/json")]  # Make it iterable as key-value pairs
            response.status_code = 201

            with patch.object(app.logger, "info") as mock_logger:
                after_request(response)

                call_args = mock_logger.call_args
                extra_data = call_args[1]["extra"]

                # Check request data
                assert "request" in extra_data
                request_data = extra_data["request"]
                assert request_data["method"] == "POST"
                assert request_data["path_info"] == "/api/test"

                # Check headers are included (transformed)
                assert "headers" in request_data
                headers = request_data["headers"]
                assert "user_agent" in headers
                assert headers["user_agent"] == "test-agent"

                # Check response data
                assert "response" in extra_data
                response_data = extra_data["response"]
                assert response_data["status_code"] == 201
                assert "time_ms" in response_data

    def test_after_request_filters_sensitive_headers(self):
        """Test that after_request filters out sensitive headers."""
        app = Flask(__name__)

        with app.test_request_context("/", headers={"Cookie": "secret=value"}):
            g.flask_remote_logging = time.time()

            # Create a mock response with sensitive headers
            response = MagicMock()
            response.headers = [("Set-Cookie", "session=abc123")]  # Make it iterable as key-value pairs
            response.status_code = 200

            with patch.object(app.logger, "info") as mock_logger:
                after_request(response)

                call_args = mock_logger.call_args
                extra_data = call_args[1]["extra"]

                # Check that cookie headers are filtered out
                request_headers = extra_data["request"]["headers"]
                assert "cookie" not in request_headers

                response_headers = extra_data["response"]["headers"]
                assert "set-cookie" not in response_headers

    def test_after_request_includes_flask_data(self):
        """Test that after_request includes Flask-specific data."""
        app = Flask(__name__)

        with app.test_request_context("/test"):
            from flask import g

            g.flask_remote_logging = time.time()

            response = MagicMock()
            response.headers = [("Content-Type", "text/html")]  # Make it iterable
            response.status_code = 200

            with patch.object(app.logger, "info") as mock_logger:
                # Patch the middleware's access to request.endpoint and view_args
                with patch("src.flask_remote_logging.middleware.request") as mock_request:
                    mock_request.endpoint = "test_endpoint"
                    mock_request.view_args = {"user_id": 123}
                    mock_request.environ = {"REQUEST_METHOD": "GET", "PATH_INFO": "/test"}

                    after_request(response)

                    call_args = mock_logger.call_args
                    extra_data = call_args[1]["extra"]

                    # Check Flask-specific data
                    assert "flask" in extra_data
                    flask_data = extra_data["flask"]
                    assert flask_data["endpoint"] == "test_endpoint"
                    assert flask_data["view_args"] == {"user_id": 123}


class TestMiddlewareIntegration:
    """Integration tests for middleware with extensions."""

    def test_middleware_with_graylog_extension(self):
        """Test middleware integration with GraylogExtension."""
        from src.flask_remote_logging import GraylogExtension

        app = Flask(__name__)
        app.config.update({"GRAYLOG_HOST": "localhost", "GRAYLOG_PORT": 12201})

        # Initialize extension with middleware enabled
        graylog = GraylogExtension(app, enable_middleware=True)

        # Verify middleware was set up
        assert len(app.before_request_funcs[None]) > 0
        assert len(app.after_request_funcs[None]) > 0

    def test_middleware_disabled(self):
        """Test that middleware can be disabled."""
        from src.flask_remote_logging import GraylogExtension

        app = Flask(__name__)
        app.config.update({"GRAYLOG_HOST": "localhost", "GRAYLOG_PORT": 12201})

        # Count existing middleware
        before_count = len(app.before_request_funcs.get(None, []))
        after_count = len(app.after_request_funcs.get(None, []))

        # Initialize extension with middleware disabled
        graylog = GraylogExtension(app, enable_middleware=False)

        # Verify middleware was not added
        assert len(app.before_request_funcs.get(None, [])) == before_count
        assert len(app.after_request_funcs.get(None, [])) == after_count

    @pytest.mark.parametrize(
        "extension_class,config",
        [
            (
                "AWSLogExtension",
                {
                    "AWS_ACCESS_KEY_ID": "test",
                    "AWS_SECRET_ACCESS_KEY": "test",
                    "AWS_REGION": "us-east-1",
                    "AWS_LOG_GROUP": "test-group",
                    "AWS_LOG_STREAM": "test-stream",
                },
            ),
            (
                "AzureLogExtension",
                {
                    "AZURE_WORKSPACE_ID": "test-id",
                    "AZURE_WORKSPACE_KEY": "test-key",
                    "AZURE_LOG_TYPE": "TestLogs",
                    "AZURE_ENVIRONMENT": "azure",
                },
            ),
            ("GCPLogExtension", {"GCP_PROJECT_ID": "test-project", "GCP_ENVIRONMENT": "gcp"}),
            (
                "IBMLogExtension",
                {"IBM_LOGDNA_INGESTION_KEY": "test-key", "IBM_LOGDNA_HOSTNAME": "test-host", "IBM_ENVIRONMENT": "ibm"},
            ),
            ("OCILogExtension", {"OCI_LOG_ID": "test-log-id", "OCI_ENVIRONMENT": "oci"}),
        ],
    )
    def test_middleware_with_all_extensions(self, extension_class, config):
        """Test middleware integration with all extensions."""
        # Import the extension class dynamically
        module = __import__("src.flask_remote_logging", fromlist=[extension_class])
        ExtensionClass = getattr(module, extension_class)

        app = Flask(__name__)
        app.config.update(config)

        # Count existing middleware
        before_count = len(app.before_request_funcs.get(None, []))
        after_count = len(app.after_request_funcs.get(None, []))

        # Initialize extension with middleware enabled
        extension = ExtensionClass(app, enable_middleware=True)

        # Verify middleware was added (should be at least one more)
        assert len(app.before_request_funcs.get(None, [])) >= before_count + 1
        assert len(app.after_request_funcs.get(None, [])) >= after_count + 1

    def test_middleware_config_override(self):
        """Test that middleware can be controlled via Flask config."""
        from src.flask_remote_logging import GraylogExtension

        app = Flask(__name__)
        app.config.update(
            {"GRAYLOG_HOST": "localhost", "GRAYLOG_PORT": 12201, "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE": False}
        )

        # Count existing middleware
        before_count = len(app.before_request_funcs.get(None, []))
        after_count = len(app.after_request_funcs.get(None, []))

        # Initialize extension (middleware should be disabled by config)
        graylog = GraylogExtension(app, enable_middleware=True)

        # Verify middleware was not added due to config override
        assert len(app.before_request_funcs.get(None, [])) == before_count
        assert len(app.after_request_funcs.get(None, [])) == after_count

    def test_middleware_end_to_end(self):
        """Test middleware functionality end-to-end with a real request."""
        from src.flask_remote_logging import GraylogExtension

        app = Flask(__name__)
        app.config.update({"GRAYLOG_HOST": "localhost", "GRAYLOG_PORT": 12201, "TESTING": True})

        @app.route("/test")
        def test_route():
            return jsonify({"message": "test"})

        # Initialize extension with middleware
        graylog = GraylogExtension(app, enable_middleware=True)

        with app.test_client() as client:
            with patch.object(app.logger, "info") as mock_logger:
                response = client.get("/test")

                # Verify the request was successful
                assert response.status_code == 200

                # Verify that middleware logged the request
                # Should have multiple log calls (from middleware and potentially others)
                assert mock_logger.called

                # Find the middleware log call
                middleware_call = None
                for call in mock_logger.call_args_list:
                    if len(call[0]) > 0 and "Finishing request" in call[0][0]:
                        middleware_call = call
                        break

                assert middleware_call is not None, "Middleware should have logged the request"

                # Verify the log contains expected data
                extra_data = middleware_call[1].get("extra", {})
                assert "response" in extra_data
                assert "request" in extra_data
                assert extra_data["response"]["status_code"] == 200
