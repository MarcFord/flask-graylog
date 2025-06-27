"""
Tests for Oracle Cloud Infrastructure (OCI) Logging Extension

This module contains comprehensive tests for the OCILogExtension class,
ensuring proper functionality for OCI Logging integration.
"""

import logging
from unittest.mock import Mock, patch

import pytest
from flask import Flask

from flask_network_logging.oci_extension import OCILogExtension, OCILogHandler


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
        app.config.update({
            "OCI_LOG_GROUP_ID": "ocid1.loggroup.oc1...",
            "OCI_LOG_ID": "ocid1.log.oc1...",
            "OCI_ENVIRONMENT": "production"
        })

        with patch("flask_network_logging.oci_extension.oci"):
            extension = OCILogExtension(app=app)

        assert extension.app == app

    def test_init_with_parameters(self):
        """Test extension initialization with custom parameters."""
        extension = OCILogExtension(
            log_level=logging.DEBUG,
            additional_logs=["custom.logger"],
            enable_middleware=False
        )

        assert extension.log_level == logging.DEBUG
        assert extension.additional_logs == ["custom.logger"]
        assert extension.enable_middleware is False

    def test_get_config_from_app_without_app(self):
        """Test configuration extraction without Flask app."""
        extension = OCILogExtension()
        extension.app = None

        config = extension._get_config_from_app()

        assert config == {}

    def test_should_skip_setup_development_environment(self):
        """Test setup skipping in development environment."""
        extension = OCILogExtension()
        extension.config = {"OCI_ENVIRONMENT": "development"}

        assert extension._should_skip_setup() is True

    def test_extension_name(self):
        """Test extension name getter."""
        extension = OCILogExtension()
        assert extension._get_extension_name() == "OCI Logging"


class TestOCILogHandler:
    """Test suite for OCILogHandler class."""

    def test_init(self):
        """Test handler initialization."""
        mock_client = Mock()
        handler = OCILogHandler(
            logging_client=mock_client,
            log_group_id="ocid1.loggroup.oc1...",
            log_id="ocid1.log.oc1...",
            app_name="test-app"
        )

        assert handler.logging_client == mock_client
        assert handler.log_group_id == "ocid1.loggroup.oc1..."
        assert handler.log_id == "ocid1.log.oc1..."
        assert handler.app_name == "test-app"

    def test_init_with_defaults(self):
        """Test handler initialization with default values."""
        mock_client = Mock()
        handler = OCILogHandler(
            logging_client=mock_client,
            log_group_id="ocid1.loggroup.oc1...",
            log_id="ocid1.log.oc1..."
        )

        assert handler.app_name == "flask-app"
