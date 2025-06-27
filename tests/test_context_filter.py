"""Tests for the FlaskRemoteLoggingContextFilter class."""

import logging
import platform
import uuid
from unittest.mock import Mock, patch

import pytest
from flask import Flask, g

from flask_remote_logging.context_filter import FlaskRemoteLoggingContextFilter


class TestFlaskRemoteLoggingContextFilter:
    """Test cases for the FlaskRemoteLoggingContextFilter class."""

    def test_init(self, mock_get_current_user):
        """Test filter initialization."""
        filter_instance = FlaskRemoteLoggingContextFilter(get_current_user=mock_get_current_user)

        assert filter_instance.get_current_user is mock_get_current_user
        assert filter_instance._FlaskRemoteLoggingContextFilter__request is None
        assert filter_instance._FlaskRemoteLoggingContextFilter__request_id is None

    def test_init_without_get_current_user(self):
        """Test filter initialization without get_current_user function."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        assert filter_instance.get_current_user is None

    def test_filter_fields(self):
        """Test that sensitive fields are properly defined."""
        expected_fields = (
            "card_number",
            "ccnum",
            "new_card-ccnum",
            "password",
            "password_confirm",
        )

        assert FlaskRemoteLoggingContextFilter.FILTER_FIELDS == expected_fields

    def test_request_property_with_context(self, app):
        """Test request property when in request context."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test"):
            request_obj = filter_instance.request
            assert request_obj is not None
            assert request_obj.path == "/test"

    def test_request_property_without_context(self):
        """Test request property when not in request context."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        request_obj = filter_instance.request
        assert request_obj is None

    def test_request_id_from_g(self, app):
        """Test request ID retrieval from Flask g object."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test"):
            g.request_id = "test-request-id-from-g"
            request_id = filter_instance.request_id
            assert request_id == "test-request-id-from-g"

    def test_request_id_from_x_request_id_header(self, app):
        """Test request ID retrieval from X-Request-ID header."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test", headers={"X-Request-ID": "test-request-id-header"}):
            request_id = filter_instance.request_id
            assert request_id == "test-request-id-header"

    def test_request_id_from_request_id_header(self, app):
        """Test request ID retrieval from Request-ID header."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test", headers={"Request-ID": "test-request-id-header2"}):
            request_id = filter_instance.request_id
            assert request_id == "test-request-id-header2"

    def test_request_id_from_x_requestid_header(self, app):
        """Test request ID retrieval from X-RequestId header."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test", headers={"X-RequestId": "test-request-id-header3"}):
            request_id = filter_instance.request_id
            assert request_id == "test-request-id-header3"

    def test_request_id_generated_uuid(self, app):
        """Test request ID generation when no ID is provided."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test"):
            with patch("uuid.uuid4") as mock_uuid:
                mock_uuid.return_value.hex = "generated-uuid-hex"
                request_id = filter_instance.request_id
                assert request_id == "generated-uuid-hex"
                mock_uuid.assert_called_once()

    def test_request_id_without_request(self):
        """Test request ID when no request context exists."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        request_id = filter_instance.request_id
        assert request_id is None

    def test_filter_method(self, app, log_record):
        """Test the main filter method."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test", query_string="param1=value1"):
            result = filter_instance.filter(log_record)

            assert result is True
            assert hasattr(log_record, "hostname")
            assert hasattr(log_record, "get_params")
            assert hasattr(log_record, "request_id")

    def test_add_host_info(self, log_record):
        """Test adding host information to log record."""
        filter_instance = FlaskRemoteLoggingContextFilter()
        filter_instance._add_host_info(log_record)

        assert log_record.hostname == platform.node()
        assert log_record.os == platform.system()
        assert log_record.os_version == platform.release()
        assert log_record.python_version == platform.python_version()
        assert log_record.python_implementation == platform.python_implementation()

    def test_add_get_params_with_request(self, app, log_record):
        """Test adding GET parameters when request exists."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test?param1=value1&param2=value2"):
            filter_instance._add_get_params(log_record)

            assert hasattr(log_record, "get_params")
            assert hasattr(log_record, "param1")
            assert hasattr(log_record, "param2")
            assert log_record.param1 == "value1"
            assert log_record.param2 == "value2"

    def test_add_get_params_without_request(self, log_record):
        """Test adding GET parameters when no request exists."""
        filter_instance = FlaskRemoteLoggingContextFilter()
        filter_instance._add_get_params(log_record)

        assert log_record.no_request == "True"

    def test_add_get_params_filters_sensitive_fields(self, app, log_record):
        """Test that sensitive fields are filtered in GET parameters."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test?password=secret123&username=testuser"):
            filter_instance._add_get_params(log_record)

            # Password should be masked, username should not
            assert log_record.password == "*********"  # 9 asterisks for 'secret123'
            assert log_record.username == "testuser"

    def test_add_request_id_with_request(self, app, log_record):
        """Test adding request ID when request exists."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test", headers={"X-Request-ID": "test-id"}):
            filter_instance._add_request_id(log_record)

            assert log_record.request_id == "test-id"

    def test_add_request_id_without_request(self, log_record):
        """Test adding request ID when no request exists."""
        filter_instance = FlaskRemoteLoggingContextFilter()
        filter_instance._add_request_id(log_record)

        assert log_record.no_request == "True"

    def test_add_request_data_with_request(self, app, log_record, request_headers):
        """Test adding request data when request exists."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test", headers=request_headers):
            filter_instance._add_request_data(log_record)

            assert hasattr(log_record, "client_ip_address")
            assert hasattr(log_record, "user_agent")
            assert hasattr(log_record, "user_os")
            assert hasattr(log_record, "user_browser")
            assert hasattr(log_record, "user_browser_version")
            assert hasattr(log_record, "user_mobile")
            assert hasattr(log_record, "url")
            assert hasattr(log_record, "request_method")

            assert log_record.request_method == "GET"
            assert log_record.url.endswith("/test")

    def test_add_request_data_without_request(self, log_record):
        """Test adding request data when no request exists."""
        filter_instance = FlaskRemoteLoggingContextFilter()
        filter_instance._add_request_data(log_record)

        assert log_record.no_request == "True"

    def test_add_user_info_with_user_object(self, log_record, mock_get_current_user, mock_user):
        """Test adding user information from user object."""
        filter_instance = FlaskRemoteLoggingContextFilter(get_current_user=mock_get_current_user)
        filter_instance._add_user_info(log_record)

        assert log_record.id == "123"
        assert log_record.uuid == "test-uuid-123"
        assert log_record.username == "testuser"
        assert log_record.email == "test@example.com"

    def test_add_user_info_with_user_dict(self, log_record, mock_get_current_user_dict):
        """Test adding user information from user dictionary."""
        filter_instance = FlaskRemoteLoggingContextFilter(get_current_user=mock_get_current_user_dict)
        filter_instance._add_user_info(log_record)

        assert log_record.id == "456"
        assert log_record.uuid == "test-uuid-456"
        assert log_record.username == "testuser2"
        assert log_record.email == "test2@example.com"

    def test_add_user_info_without_get_current_user(self, log_record):
        """Test adding user information when get_current_user is not provided."""
        filter_instance = FlaskRemoteLoggingContextFilter()
        filter_instance._add_user_info(log_record)

        # Should not add any user attributes
        assert not hasattr(log_record, "id")
        assert not hasattr(log_record, "username")
        assert not hasattr(log_record, "email")

    def test_add_user_info_with_non_callable_get_current_user(self, log_record):
        """Test adding user information when get_current_user is not callable."""
        filter_instance = FlaskRemoteLoggingContextFilter(get_current_user="not_callable")
        filter_instance._add_user_info(log_record)

        # Should not add any user attributes
        assert not hasattr(log_record, "id")
        assert not hasattr(log_record, "username")
        assert not hasattr(log_record, "email")

    def test_add_user_info_partial_user_data(self, log_record):
        """Test adding user information with partial user data."""
        partial_user = Mock()
        partial_user.id = "789"
        # Missing other attributes - make sure they don't exist
        del partial_user.username
        del partial_user.email
        del partial_user.uuid

        def get_partial_user():
            return partial_user

        filter_instance = FlaskRemoteLoggingContextFilter(get_current_user=get_partial_user)
        filter_instance._add_user_info(log_record)

        assert log_record.id == "789"
        assert not hasattr(log_record, "username")
        assert not hasattr(log_record, "email")
        assert not hasattr(log_record, "uuid")

    def test_add_user_info_existing_attributes(self, log_record, mock_get_current_user):
        """Test that existing attributes are not overwritten."""
        log_record.id = "existing-id"

        filter_instance = FlaskRemoteLoggingContextFilter(get_current_user=mock_get_current_user)
        filter_instance._add_user_info(log_record)

        # Should not overwrite existing attribute
        assert log_record.id == "existing-id"
        # But should add missing ones
        assert log_record.username == "testuser"

    def test_get_ip_address_from_x_forwarded_for_environ(self, app):
        """Test IP address retrieval from HTTP_X_FORWARDED_FOR environment."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test", environ_base={"HTTP_X_FORWARDED_FOR": "192.168.1.100"}):
            ip = filter_instance._FlaskRemoteLoggingContextFilter__get_ip_address()
            assert ip == "192.168.1.100"

    def test_get_ip_address_from_remote_addr_environ(self, app):
        """Test IP address retrieval from REMOTE_ADDR environment."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test", environ_base={"REMOTE_ADDR": "192.168.1.101"}):
            ip = filter_instance._FlaskRemoteLoggingContextFilter__get_ip_address()
            assert ip == "192.168.1.101"

    def test_get_ip_address_from_x_real_ip_environ(self, app):
        """Test IP address retrieval from HTTP_X_REAL_IP environment."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test", environ_base={"HTTP_X_REAL_IP": "192.168.1.102"}):
            ip = filter_instance._FlaskRemoteLoggingContextFilter__get_ip_address()
            assert ip == "192.168.1.102"

    def test_get_ip_address_from_headers(self, app):
        """Test IP address retrieval from request headers."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test", headers={"X-Forwarded-For": "192.168.1.103"}):
            ip = filter_instance._FlaskRemoteLoggingContextFilter__get_ip_address()
            assert ip == "192.168.1.103"

    def test_get_ip_address_from_remote_addr(self, app):
        """Test IP address retrieval from request.remote_addr."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test"):
            # Mock the Flask request
            with patch("flask_remote_logging.context_filter.request") as mock_request:
                mock_request.environ = {}
                mock_request.headers = {}
                mock_request.remote_addr = "127.0.0.1"

                ip = filter_instance._FlaskRemoteLoggingContextFilter__get_ip_address()
                assert ip == "127.0.0.1"

    def test_get_ip_address_without_request(self):
        """Test IP address retrieval when no request exists."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        ip = filter_instance._FlaskRemoteLoggingContextFilter__get_ip_address()
        assert ip is None

    def test_get_client_data_with_request(self, app, request_headers):
        """Test client data retrieval when request exists."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test", headers=request_headers):
            with patch.object(filter_instance, "_get_client_ip", return_value="192.168.1.100"):
                client_data = filter_instance._FlaskRemoteLoggingContextFilter__get_client_data()

                assert "ip_address" in client_data
                assert "browser" in client_data
                assert "os" in client_data
                assert "mobile" in client_data

                assert client_data["ip_address"] == "192.168.1.100"
                assert "name" in client_data["browser"]
                assert "version" in client_data["browser"]

    def test_get_client_data_without_request(self):
        """Test client data retrieval when no request exists."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        client_data = filter_instance._FlaskRemoteLoggingContextFilter__get_client_data()
        assert client_data == {}

    def test_filter_param_fields(self):
        """Test filtering of sensitive parameter fields."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        params = {
            "username": "testuser",
            "password": "secret123",
            "card_number": "1234567890123456",
            "email": "test@example.com",
        }

        filtered = filter_instance._FlaskRemoteLoggingContextFilter__filter_param_fields(params)

        assert filtered["username"] == "testuser"
        assert filtered["password"] == "*********"  # 9 asterisks
        assert filtered["card_number"] == "****************"  # 16 asterisks
        assert filtered["email"] == "test@example.com"

    def test_filter_param_fields_empty_dict(self):
        """Test filtering of empty parameter dictionary."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        filtered = filter_instance._FlaskRemoteLoggingContextFilter__filter_param_fields({})
        assert filtered == {}

    def test_get_client_ip_calls_get_ip_address(self, app):
        """Test that _get_client_ip correctly calls __get_ip_address."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test", headers={"X-Forwarded-For": "192.168.1.100"}):
            ip = filter_instance._get_client_ip()
            assert ip == "192.168.1.100"

    def test_user_info_with_string_conversion_error(self, log_record):
        """Test user info addition when string conversion fails."""
        problematic_user = Mock()
        problematic_user.id = Mock()
        problematic_user.id.__str__ = Mock(side_effect=Exception("String conversion error"))
        problematic_user.username = "testuser"

        def get_problematic_user():
            return problematic_user

        filter_instance = FlaskRemoteLoggingContextFilter(get_current_user=get_problematic_user)
        filter_instance._add_user_info(log_record)

        # Should skip the problematic field but add others
        assert not hasattr(log_record, "id")
        assert log_record.username == "testuser"

    def test_request_id_header_precedence(self, app):
        """Test that request ID headers are checked in correct precedence."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        # Test that g.request_id takes precedence
        with app.test_request_context("/test", headers={"X-Request-ID": "header-id"}):
            g.request_id = "g-request-id"
            request_id = filter_instance.request_id
            assert request_id == "g-request-id"

    def test_multiple_calls_same_request_id(self, app):
        """Test that multiple calls return the same request ID."""
        filter_instance = FlaskRemoteLoggingContextFilter()

        with app.test_request_context("/test", headers={"X-Request-ID": "consistent-id"}):
            first_call = filter_instance.request_id
            second_call = filter_instance.request_id
            assert first_call == second_call == "consistent-id"
