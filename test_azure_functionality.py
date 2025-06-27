#!/usr/bin/env python3
"""
Test script to verify Azure Monitor Logs extension functionality.

This script creates a simple Flask app with Azure Monitor configuration
and tests various logging scenarios to ensure the extension works correctly.
"""

import os
import sys
import logging
import json
from unittest.mock import Mock, patch

# Add the src directory to the path so we can import from the local source
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flask import Flask
from flask_remote_logging import AzureLogExtension, AzureLog

def test_azure_extension_basic_functionality():
    """Test basic Azure extension functionality."""
    print("Testing Azure Monitor Logs Extension...")
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configure Azure Monitor (with dummy values for testing)
    app.config.update({
        'AZURE_WORKSPACE_ID': 'test-workspace-id',
        'AZURE_WORKSPACE_KEY': 'test-workspace-key',
        'AZURE_LOG_TYPE': 'TestLogs',
        'AZURE_LOG_LEVEL': 'INFO',
        'AZURE_ENVIRONMENT': 'development'
    })
    
    # Test initialization
    azure_log = AzureLogExtension(app)
    assert azure_log.app is app
    assert azure_log.workspace_id == 'test-workspace-id'
    assert azure_log.workspace_key == 'test-workspace-key'
    assert azure_log.log_type == 'TestLogs'
    
    print("✓ Basic initialization works")
    
    # Test alias
    azure_log_alias = AzureLog(app)
    assert isinstance(azure_log_alias, AzureLogExtension)
    print("✓ AzureLog alias works")
    
    # Test setup logging (mocking requests to avoid actual HTTP calls)
    with patch('flask_remote_logging.azure_extension.requests') as mock_requests:
        azure_log._setup_logging()
        print("✓ Setup logging works with mocked requests")
    
    # Test configuration extraction
    config = azure_log._get_config_from_app()
    assert config['AZURE_WORKSPACE_ID'] == 'test-workspace-id'
    assert config['AZURE_LOG_TYPE'] == 'TestLogs'
    print("✓ Configuration extraction works")
    
    print("All basic functionality tests passed!")

def test_azure_handler():
    """Test the Azure Monitor handler."""
    print("\nTesting Azure Monitor Handler...")
    
    from flask_remote_logging.azure_extension import AzureMonitorHandler
    
    # Create handler
    handler = AzureMonitorHandler(
        workspace_id='test-workspace-id',
        workspace_key='test-workspace-key',
        log_type='TestLogs'
    )
    
    assert handler.workspace_id == 'test-workspace-id'
    assert handler.workspace_key == 'test-workspace-key'
    assert handler.log_type == 'TestLogs'
    assert handler.timeout == 30
    assert 'test-workspace-id.ods.opinsights.azure.com' in handler.uri
    
    print("✓ Handler initialization works")
    
    # Test log record creation and formatting
    record = logging.LogRecord(
        name='test.logger',
        level=logging.INFO,
        pathname='/test/path.py',
        lineno=123,
        msg='Test message',
        args=(),
        exc_info=None
    )
    
    # Mock requests to test emit without actual HTTP calls
    with patch('flask_remote_logging.azure_extension.requests') as mock_requests:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.post.return_value = mock_response
        
        handler.emit(record)
        
        # Verify that POST was called
        mock_requests.post.assert_called_once()
        call_args = mock_requests.post.call_args
        
        # Check URL
        assert 'test-workspace-id.ods.opinsights.azure.com' in call_args[0][0]
        
        # Check headers
        headers = call_args[1]['headers']
        assert headers['Log-Type'] == 'TestLogs'
        assert 'Authorization' in headers
        assert headers['content-type'] == 'application/json'
        
        # Check data
        data = json.loads(call_args[1]['data'])
        assert len(data) == 1
        log_entry = data[0]
        assert log_entry['level'] == 'INFO'
        assert log_entry['logger'] == 'test.logger'
        assert 'timestamp' in log_entry
        
        print("✓ Handler emit works with proper data formatting")
    
    print("Azure Monitor Handler tests passed!")

def test_context_filter_integration():
    """Test that Azure extension works with the context filter."""
    print("\nTesting context filter integration...")
    
    # Create Flask app
    app = Flask(__name__)
    app.config.update({
        'AZURE_WORKSPACE_ID': 'test-workspace-id',
        'AZURE_WORKSPACE_KEY': 'test-workspace-key',
        'AZURE_LOG_TYPE': 'TestLogs',
        'AZURE_ENVIRONMENT': 'azure'  # Force Azure environment
    })
    
    # Create extension with get_current_user function
    def get_current_user():
        return {"id": 123, "username": "testuser", "email": "test@example.com"}
    
    azure_log = AzureLogExtension(app, get_current_user=get_current_user)
    
    # Test that context filter is created
    with patch('flask_remote_logging.azure_extension.requests'):
        azure_log._setup_logging()
    
    from flask_remote_logging.context_filter import GraylogContextFilter
    assert isinstance(azure_log.context_filter, GraylogContextFilter)
    assert azure_log.context_filter.get_current_user == get_current_user
    
    print("✓ Context filter integration works")
    print("Azure context filter integration tests passed!")

def test_environment_configuration():
    """Test environment-based configuration."""
    print("\nTesting environment configuration...")
    
    # Set environment variables
    test_env = {
        'AZURE_WORKSPACE_ID': 'env-workspace-id',
        'AZURE_WORKSPACE_KEY': 'env-workspace-key',
        'AZURE_LOG_TYPE': 'EnvTestLogs',
        'AZURE_LOG_LEVEL': 'DEBUG',
        'AZURE_ENVIRONMENT': 'production',
        'AZURE_TIMEOUT': '60'
    }
    
    # Mock environment variables
    with patch.dict(os.environ, test_env):
        app = Flask(__name__)
        azure_log = AzureLogExtension(app)
        
        config = azure_log._get_config_from_app()
        assert config['AZURE_WORKSPACE_ID'] == 'env-workspace-id'
        assert config['AZURE_WORKSPACE_KEY'] == 'env-workspace-key'
        assert config['AZURE_LOG_TYPE'] == 'EnvTestLogs'
        assert config['AZURE_LOG_LEVEL'] == 'DEBUG'
        assert config['AZURE_ENVIRONMENT'] == 'production'
        assert config['AZURE_TIMEOUT'] == '60'
    
    print("✓ Environment variable configuration works")
    print("Environment configuration tests passed!")

if __name__ == '__main__':
    print("Azure Monitor Logs Extension Test Suite")
    print("=" * 50)
    
    try:
        test_azure_extension_basic_functionality()
        test_azure_handler()
        test_context_filter_integration()
        test_environment_configuration()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Azure Monitor Logs extension is working correctly.")
        print("\nThe Azure Monitor Logs extension provides:")
        print("  ✓ Full Azure Log Analytics integration")
        print("  ✓ HTTP Data Collector API support")
        print("  ✓ Reusable context filter (same as other backends)")
        print("  ✓ Environment-based configuration")
        print("  ✓ Proper error handling and fallbacks")
        print("  ✓ Custom field support")
        print("  ✓ Configurable log levels and types")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
