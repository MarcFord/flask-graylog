"""Performance and edge case tests for flask-graylog."""

import logging
import time
from unittest.mock import Mock, patch

import pytest
from flask import Flask

from flask_remote_logging import FlaskRemoteLoggingContextFilter, GraylogExtension


class TestPerformanceAndEdgeCases:
    """Test performance characteristics and edge cases."""

    def test_large_number_of_parameters(self, app):
        """Test handling of large number of request parameters."""
        filter_instance = FlaskRemoteLoggingContextFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Create a large query string
        large_params = {f"param{i}": f"value{i}" for i in range(100)}
        query_string = "&".join(f"{k}={v}" for k, v in large_params.items())

        with app.test_request_context(f"/test?{query_string}"):
            # This should complete without performance issues
            start_time = time.time()
            filter_instance._add_get_params(log_record)
            end_time = time.time()

            # Should complete in reasonable time (< 1 second)
            assert end_time - start_time < 1.0
            assert hasattr(log_record, "get_params")

    def test_very_long_user_agent(self, app):
        """Test handling of very long user agent strings."""
        filter_instance = FlaskRemoteLoggingContextFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Create a very long user agent string
        long_user_agent = "A" * 10000

        with app.test_request_context("/test", headers={"User-Agent": long_user_agent}):
            filter_instance._add_request_data(log_record)

            assert hasattr(log_record, "user_agent")
            assert len(log_record.user_agent) == 10000

    def test_unicode_parameters(self, app):
        """Test handling of unicode characters in parameters."""
        filter_instance = FlaskRemoteLoggingContextFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        unicode_params = {"user_name": "José María", "city": "北京", "emoji": "😀🎉🚀"}
        query_string = "&".join(f"{k}={v}" for k, v in unicode_params.items())

        with app.test_request_context(f"/test?{query_string}"):
            filter_instance._add_get_params(log_record)

            # Check that unicode parameters are properly added
            assert hasattr(log_record, "get_params")
            assert hasattr(log_record, "user_name")
            assert log_record.user_name == "José María"
            assert hasattr(log_record, "city")
            assert log_record.city == "北京"
            assert hasattr(log_record, "emoji")
            assert log_record.emoji == "😀🎉🚀"

    def test_malformed_user_agent(self, app):
        """Test handling of malformed user agent strings."""
        filter_instance = FlaskRemoteLoggingContextFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        malformed_user_agents = [
            "",  # Empty
            "\x00\x01\x02",  # Control characters
            "A" * 1000,  # Very long
            ";;;;;;;;;;;",  # Special characters
        ]

        for user_agent in malformed_user_agents:
            with app.test_request_context("/test", headers={"User-Agent": user_agent}):
                # Should not raise an exception
                filter_instance._add_request_data(log_record)
                assert hasattr(log_record, "user_agent")

    def test_missing_request_attributes(self, app):
        """Test handling when request object is missing expected attributes."""
        filter_instance = FlaskRemoteLoggingContextFilter()
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        with app.test_request_context("/test"):
            # Mock Flask request to simulate missing attributes
            with patch("flask_remote_logging.context_filter.request") as mock_request:
                mock_request.values = Mock()
                mock_request.values.to_dict.side_effect = AttributeError("Missing method")

                # Should handle gracefully
                filter_instance._add_get_params(log_record)
                # Should still set no_request attribute if there's an error
                assert hasattr(log_record, "no_request") or hasattr(log_record, "get_params")

    def test_extremely_deep_nested_config(self):
        """Test with deeply nested configuration values."""
        app = Flask(__name__)

        # Test with config values that might cause issues
        app.config.update(
            {
                "GRAYLOG_HOST": None,  # None value
                "GRAYLOG_PORT": "invalid",  # String instead of int
                "GRAYLOG_EXTRA_FIELDS": "true",  # String instead of bool
            }
        )

        extension = GraylogExtension(app=app)
        config = extension._get_config_from_app()

        # Should handle gracefully and provide defaults or convert types
        assert config is not None
        assert isinstance(config, dict)

    def test_memory_usage_with_many_log_records(self, app):
        """Test memory usage doesn't grow excessively with many log records."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        # Process many log records
        for i in range(1000):
            log_record = logging.LogRecord(
                name=f"test{i}",
                level=logging.INFO,
                pathname="/test/path.py",
                lineno=42,
                msg=f"Test message {i}",
                args=(),
                exc_info=None,
            )

            with app.test_request_context(f"/test{i}"):
                result = filter_instance.filter(log_record)
                assert result is True

        # Filter should not maintain state that grows with number of records
        # (This is more of a behavioral test - in a real scenario you'd use memory profilers)

    def test_concurrent_request_contexts(self, app):
        """Test behavior with multiple request contexts."""
        filter1 = FlaskRemoteLoggingContextFilter()
        filter2 = FlaskRemoteLoggingContextFilter()

        log_record1 = logging.LogRecord(
            name="test1",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message 1",
            args=(),
            exc_info=None,
        )

        log_record2 = logging.LogRecord(
            name="test2",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message 2",
            args=(),
            exc_info=None,
        )

        # Simulate overlapping contexts (though Flask doesn't support true concurrency)
        with app.test_request_context("/test1", headers={"X-Request-ID": "req1"}):
            filter1.filter(log_record1)

            with app.test_request_context("/test2", headers={"X-Request-ID": "req2"}):
                filter2.filter(log_record2)

        # Each filter should have processed its own context
        # Note: Due to Flask's context locals, this test has limitations
        # but verifies basic functionality doesn't break

    def test_extension_with_none_app_config(self):
        """Test extension when app config values are None."""
        app = Flask(__name__)
        # Clear all config to simulate missing configuration but keep essential Flask config
        app.config.clear()
        app.config.update(
            {
                "ENV": "production",
                "DEBUG": False,
                "TESTING": False,
            }
        )

        extension = GraylogExtension(app=app)
        config = extension._get_config_from_app()

        # Should provide sensible defaults
        assert config["GRAYLOG_HOST"] == "localhost"
        assert config["GRAYLOG_PORT"] == 12201
        assert config["GRAYLOG_EXTRA_FIELDS"] is True

    def test_filter_with_circular_reference_user(self):
        """Test filter with user object that has circular references."""

        def get_circular_user():
            user = Mock()
            user.id = "123"
            user.self_ref = user  # Circular reference
            return user

        filter_instance = FlaskRemoteLoggingContextFilter(get_current_user=get_circular_user)
        log_record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Should handle without infinite recursion
        filter_instance._add_user_info(log_record)
        assert log_record.id == "123"

    def test_request_id_generation_uniqueness(self, app):
        """Test that generated request IDs are unique."""
        filter_instance = FlaskRemoteLoggingContextFilter()
        request_ids = set()

        for _ in range(100):
            with app.test_request_context("/test"):
                # Reset the internal request ID to force regeneration
                filter_instance._FlaskRemoteLoggingContextFilter__request_id = None
                filter_instance._FlaskRemoteLoggingContextFilter__request = None

                request_id = filter_instance.request_id
                request_ids.add(request_id)

        # Should generate unique IDs
        assert len(request_ids) == 100

    def test_parameter_filtering_edge_cases(self):
        """Test parameter filtering with edge cases."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        edge_case_params = {
            "": "empty_key",  # Empty key
            "normal": "",  # Empty value
            "password": None,  # None value
            "card_number": 123456789,  # Numeric value
            "nested[password]": "secret",  # Nested-style parameter
        }

        filtered = filter_instance._FlaskRemoteLoggingContextFilter__filter_param_fields(edge_case_params)

        # Should handle all edge cases without crashing
        assert isinstance(filtered, dict)
        assert filtered["password"] == "****"  # 4 asterisks for 'None'
        assert filtered["card_number"] == "*********"  # 9 asterisks for the number

    def test_ip_address_extraction_edge_cases(self, app):
        """Test IP address extraction with various edge cases."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        edge_case_headers = [
            {},  # No headers
            {"X-Forwarded-For": ""},  # Empty header
            {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"},  # Multiple IPs
            {"X-Forwarded-For": "invalid-ip"},  # Invalid IP format
        ]

        for headers in edge_case_headers:
            with app.test_request_context("/test", headers=headers):
                # Should not crash
                ip = filter_instance._FlaskRemoteLoggingContextFilter__get_ip_address()
                # Should return some value or None
                assert ip is None or isinstance(ip, str)
