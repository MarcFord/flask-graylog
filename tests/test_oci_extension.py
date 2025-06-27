"""
Tests for Oracle Cloud Infrastructure (OCI) Logging Extension

This module contains comprehensive tests for the OCILogExtension class,
ensuring proper functionality for OCI Logging integration.
"""

import json
import logging
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, g, request

from flask_network_logging.oci_extension import OCILogExtension, OCILoggingHandler


class TestOCILogExtension:
    """Test suite for OCILogExtension class."""

    def test_init_without_app(self):
        """Test extension initialization without Flask app."""
        extension = OCILogExtension()
        
        assert extension.app is None
        assert extension.get_current_user is None
        assert extension.log_level == logging.INFO
        assert extension.additional_logs == []
        assert extension.context_filter is None
        assert extension.log_formatter is None
        assert extension.config == {}
        assert extension.logging_client is None

    def test_init_with_app(self):
        """Test extension initialization with Flask app."""
        app = Flask(__name__)
        
        with patch.object(OCILogExtension, 'init_app') as mock_init:
            extension = OCILogExtension(app)
            mock_init.assert_called_once_with(app)

    def test_init_app(self):
        """Test init_app method."""
        app = Flask(__name__)
        app.config.update({
            'OCI_CONFIG_PROFILE': 'DEFAULT',
            'OCI_LOG_ID': 'ocid1.log.oc1...',
            'OCI_LOG_LEVEL': 'DEBUG'
        })
        
        extension = OCILogExtension()
        
        with patch.object(extension, '_init_oci_config') as mock_init_oci:
            extension.init_app(app)
            
            assert extension.app == app
            assert extension.config['OCI_CONFIG_PROFILE'] == 'DEFAULT'
            assert extension.config['OCI_LOG_ID'] == 'ocid1.log.oc1...'
            mock_init_oci.assert_called_once()

    def test_get_config_from_app(self):
        """Test configuration extraction from Flask app."""
        app = Flask(__name__)
        app.config.update({
            'OCI_CONFIG_PROFILE': 'TEST_PROFILE',
            'OCI_LOG_GROUP_ID': 'ocid1.loggroup.oc1...',
            'OCI_LOG_ID': 'ocid1.log.oc1...',
            'OCI_SOURCE': 'test-app',
            'OCI_LOG_LEVEL': 'DEBUG',
            'OCI_ENVIRONMENT': 'production'
        })
        
        extension = OCILogExtension()
        extension.app = app
        
        config = extension._get_config_from_app()
        
        assert config['OCI_CONFIG_PROFILE'] == 'TEST_PROFILE'
        assert config['OCI_LOG_GROUP_ID'] == 'ocid1.loggroup.oc1...'
        assert config['OCI_LOG_ID'] == 'ocid1.log.oc1...'
        assert config['OCI_SOURCE'] == 'test-app'
        assert config['OCI_LOG_LEVEL'] == 'DEBUG'
        assert config['OCI_ENVIRONMENT'] == 'production'

    def test_get_config_without_app(self):
        """Test configuration extraction without Flask app."""
        extension = OCILogExtension()
        config = extension._get_config_from_app()
        assert config == {}

    @patch('flask_network_logging.oci_extension.oci', None)
    def test_init_oci_config_without_oci(self):
        """Test OCI config initialization when OCI SDK is not available."""
        app = Flask(__name__)
        extension = OCILogExtension()
        extension.app = app
        extension.config = {}
        
        with pytest.raises(ImportError, match="oci is required for Oracle Cloud Infrastructure Logging support"):
            extension._init_oci_config()

    @patch('flask_network_logging.oci_extension.oci')
    def test_init_oci_config_missing_key(self, mock_oci):
        """Test OCI config initialization with missing configuration."""
        mock_oci.config.from_file.side_effect = Exception("Config file not found")
        
        app = Flask(__name__)
        extension = OCILogExtension()
        extension.app = app
        extension.config = {}
        
        extension._init_oci_config()
        
        assert extension.logging_client is None

    @patch('flask_network_logging.oci_extension.oci')
    def test_setup_logging(self, mock_oci):
        """Test logging setup with OCI environment."""
        app = Flask(__name__)
        app.config.update({
            'OCI_ENVIRONMENT': 'oci',
            'OCI_LOG_ID': 'ocid1.log.oc1...',
            'OCI_LOG_LEVEL': 'INFO'
        })
        
        extension = OCILogExtension()
        extension.app = app
        extension.logging_client = Mock()
        extension._configure_logger = Mock()
        
        extension._setup_logging()
        
        # Should configure the main logger
        extension._configure_logger.assert_called_with(app.logger, logging.INFO)

    def test_setup_logging_development_env(self):
        """Test logging setup skips in development environment."""
        app = Flask(__name__)
        app.config.update({
            'OCI_ENVIRONMENT': 'development'
        })
        
        extension = OCILogExtension()
        extension.app = app
        extension._configure_logger = Mock()
        
        extension._setup_logging()
        
        # Should not configure logger in development
        extension._configure_logger.assert_not_called()

    @patch('flask_network_logging.oci_extension.oci')
    def test_configure_logger_with_handler(self, mock_oci):
        """Test logger configuration with OCI handler."""
        app = Flask(__name__)
        extension = OCILogExtension()
        extension.app = app
        extension.config = {
            'OCI_LOG_ID': 'ocid1.log.oc1...',
            'OCI_SOURCE': 'test-app'
        }
        extension.logging_client = Mock()
        extension.log_formatter = logging.Formatter()
        extension.context_filter = Mock()
        
        logger = Mock()
        logger.handlers = []
        
        with patch('flask_network_logging.oci_extension.OCILoggingHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            
            extension._configure_logger(logger, logging.INFO)
            
            logger.setLevel.assert_called_with(logging.INFO)
            mock_handler_class.assert_called_once()
            mock_handler.setLevel.assert_called_with(logging.INFO)
            mock_handler.addFilter.assert_called_with(extension.context_filter)
            logger.addHandler.assert_called()

    def test_configure_logger_no_key(self):
        """Test logger configuration without OCI log ID."""
        app = Flask(__name__)
        extension = OCILogExtension()
        extension.app = app
        extension.config = {}
        extension.logging_client = None
        extension.log_formatter = logging.Formatter()
        
        logger = Mock()
        logger.handlers = []
        
        extension._configure_logger(logger, logging.INFO)
        
        # Should only add stream handler
        logger.setLevel.assert_called_with(logging.INFO)
        logger.addHandler.assert_called_once()


class TestOCILoggingHandler:
    """Test suite for OCILoggingHandler class."""

    def test_init(self):
        """Test handler initialization."""
        mock_client = Mock()
        handler = OCILoggingHandler(
            client=mock_client,
            log_id='ocid1.log.oc1...',
            source='test-app'
        )
        
        assert handler.client == mock_client
        assert handler.log_id == 'ocid1.log.oc1...'
        assert handler.source == 'test-app'
        assert handler.hostname is not None

    def test_init_with_defaults(self):
        """Test handler initialization with default values."""
        mock_client = Mock()
        handler = OCILoggingHandler(client=mock_client, log_id='ocid1.log.oc1...')
        
        assert handler.source == 'flask-app'

    @patch('flask_network_logging.oci_extension.oci')
    def test_emit_success(self, mock_oci):
        """Test successful log emission."""
        mock_client = Mock()
        handler = OCILoggingHandler(
            client=mock_client,
            log_id='ocid1.log.oc1...',
            source='test-app'
        )
        handler.setFormatter(logging.Formatter('%(message)s'))
        
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        with patch.object(handler, '_send_log_entry') as mock_send:
            handler.emit(record)
            mock_send.assert_called_once()

    def test_emit_with_extra_fields(self):
        """Test log emission with extra fields."""
        mock_client = Mock()
        handler = OCILoggingHandler(
            client=mock_client,
            log_id='ocid1.log.oc1...',
            source='test-app'
        )
        handler.setFormatter(logging.Formatter('%(message)s'))
        
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )
        record.request_id = 'req-123'
        record.user_id = 'user-456'
        
        with patch.object(handler, '_send_log_entry') as mock_send:
            handler.emit(record)
            
            args, kwargs = mock_send.call_args
            log_entry = args[0]
            
            assert 'extra' in log_entry
            extra_data = json.loads(log_entry['extra'])
            assert extra_data['request_id'] == 'req-123'
            assert extra_data['user_id'] == 'user-456'

    def test_emit_error_response(self):
        """Test log emission with OCI API error."""
        mock_client = Mock()
        handler = OCILoggingHandler(
            client=mock_client,
            log_id='ocid1.log.oc1...',
            source='test-app'
        )
        handler.setFormatter(logging.Formatter('%(message)s'))
        
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        with patch.object(handler, '_send_log_entry', side_effect=Exception("API Error")):
            with patch.object(handler, 'handleError') as mock_handle_error:
                handler.emit(record)
                mock_handle_error.assert_called_once_with(record)

    @patch('flask_network_logging.oci_extension.oci', None)
    def test_send_log_data_without_oci(self):
        """Test sending log data without OCI SDK."""
        handler = OCILoggingHandler(
            client=Mock(),
            log_id='ocid1.log.oc1...',
            source='test-app'
        )
        
        log_entry = {'message': 'test', 'timestamp': '2023-01-01T00:00:00Z'}
        
        with pytest.raises(ImportError, match="OCI SDK is required"):
            handler._send_log_entry(log_entry)

    @patch('flask_network_logging.oci_extension.oci')
    def test_send_log_data_success(self, mock_oci):
        """Test successful log data sending."""
        mock_client = Mock()
        handler = OCILoggingHandler(
            client=mock_client,
            log_id='ocid1.log.oc1...',
            source='test-app'
        )
        
        log_entry = {
            'message': 'test message',
            'timestamp': '2023-01-01T00:00:00Z',
            'level': 'INFO'
        }
        
        handler._send_log_entry(log_entry)
        
        mock_client.put_logs.assert_called_once()
        call_args = mock_client.put_logs.call_args
        assert call_args.kwargs['log_id'] == 'ocid1.log.oc1...'

    @patch('flask_network_logging.oci_extension.oci')
    def test_send_log_data_with_optional_params(self, mock_oci):
        """Test log data sending with optional parameters."""
        mock_client = Mock()
        handler = OCILoggingHandler(
            client=mock_client,
            log_id='ocid1.log.oc1...',
            source='custom-source'
        )
        
        log_entry = {
            'message': 'test message',
            'timestamp': '2023-01-01T00:00:00Z',
            'level': 'INFO',
            'extra': '{"custom_field": "value"}'
        }
        
        handler._send_log_entry(log_entry)
        
        mock_client.put_logs.assert_called_once()

    def test_map_log_level(self):
        """Test log level mapping."""
        handler = OCILoggingHandler(
            client=Mock(),
            log_id='ocid1.log.oc1...',
            source='test-app'
        )
        
        assert handler._map_log_level('DEBUG') == 'DEBUG'
        assert handler._map_log_level('INFO') == 'INFO'
        assert handler._map_log_level('WARNING') == 'WARN'
        assert handler._map_log_level('ERROR') == 'ERROR'
        assert handler._map_log_level('CRITICAL') == 'FATAL'
        assert handler._map_log_level('UNKNOWN') == 'INFO'

    @patch('flask_network_logging.oci_extension.oci')
    def test_handler_integration(self, mock_oci):
        """Test complete handler integration."""
        app = Flask(__name__)
        
        with app.app_context():
            mock_client = Mock()
            handler = OCILoggingHandler(
                client=mock_client,
                log_id='ocid1.log.oc1...',
                source='test-app'
            )
            handler.setFormatter(logging.Formatter('%(message)s'))
            
            logger = logging.getLogger('test-logger')
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            
            # Test that logging works
            logger.info("Test integration message")
            
            # Verify the handler was called
            mock_client.put_logs.assert_called_once()
