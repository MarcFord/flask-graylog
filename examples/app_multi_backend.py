#!/usr/bin/env python3
"""
Flask Network Logging Multi-Backend Example

This example demonstrates how to use the flask-network-logging extension to send logs
to multiple remote logging services from a Flask application, including all supported backends.

Features demonstrated:
- Graylog setup and configuration
- Google Cloud Logging setup and configuration  
- AWS CloudWatch Logs setup and configuration
- Azure Monitor Logs setup and configuration
- IBM Cloud Logs setup and configuration
- Using multiple extensions simultaneously
- Different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Custom fields in log messages
- Error handling with automatic logging
- Request context logging
- Environment-based configuration
"""

import os
import random
import time
import uuid
from datetime import datetime

from flask import Flask, jsonify, request, g

from flask_remote_logging import GraylogExtension, GCPLogExtension, AWSLogExtension, AzureLogExtension, IBMLogExtension, OCILogExtension

# Create Flask application
app = Flask(__name__)

# Configuration for multiple logging backends
app.config.update({
    # Graylog server configuration
    'GRAYLOG_HOST': os.getenv('GRAYLOG_HOST', 'localhost'),
    'GRAYLOG_PORT': int(os.getenv('GRAYLOG_PORT', 12201)),
    'GRAYLOG_LEVEL': os.getenv('GRAYLOG_LEVEL', 'INFO'),
    'GRAYLOG_ENVIRONMENT': os.getenv('GRAYLOG_ENVIRONMENT', 'development'),
    
    # Google Cloud Logging configuration
    'GCP_PROJECT_ID': os.getenv('GCP_PROJECT_ID'),
    'GCP_CREDENTIALS_PATH': os.getenv('GCP_CREDENTIALS_PATH'),
    'GCP_LOG_NAME': os.getenv('GCP_LOG_NAME', 'flask-network-logging-example'),
    'GCP_LOG_LEVEL': os.getenv('GCP_LOG_LEVEL', 'INFO'),
    'GCP_ENVIRONMENT': os.getenv('GCP_ENVIRONMENT', 'development'),
    
    # AWS CloudWatch Logs configuration
    'AWS_REGION': os.getenv('AWS_REGION', 'us-east-1'),
    'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
    'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
    'AWS_LOG_GROUP': os.getenv('AWS_LOG_GROUP', '/flask-app/logs'),
    'AWS_LOG_STREAM': os.getenv('AWS_LOG_STREAM', 'multi-backend-example'),
    'AWS_LOG_LEVEL': os.getenv('AWS_LOG_LEVEL', 'INFO'),
    'AWS_ENVIRONMENT': os.getenv('AWS_ENVIRONMENT', 'development'),
    
    # Azure Monitor Logs configuration
    'AZURE_WORKSPACE_ID': os.getenv('AZURE_WORKSPACE_ID'),
    'AZURE_WORKSPACE_KEY': os.getenv('AZURE_WORKSPACE_KEY'),
    'AZURE_LOG_TYPE': os.getenv('AZURE_LOG_TYPE', 'FlaskMultiBackendLogs'),
    'AZURE_LOG_LEVEL': os.getenv('AZURE_LOG_LEVEL', 'INFO'),
    'AZURE_ENVIRONMENT': os.getenv('AZURE_ENVIRONMENT', 'development'),
    'AZURE_TIMEOUT': os.getenv('AZURE_TIMEOUT', '30'),
    
    # IBM Cloud Logs configuration
    'IBM_INGESTION_KEY': os.getenv('IBM_INGESTION_KEY'),
    'IBM_HOSTNAME': os.getenv('IBM_HOSTNAME'),
    'IBM_APP_NAME': os.getenv('IBM_APP_NAME', 'FlaskMultiBackendLogs'),
    'IBM_ENV': os.getenv('IBM_ENV', 'development'),
    'IBM_LOG_LEVEL': os.getenv('IBM_LOG_LEVEL', 'INFO'),
    'IBM_ENVIRONMENT': os.getenv('IBM_ENVIRONMENT', 'development'),
    'IBM_TAGS': os.getenv('IBM_TAGS', 'flask,multi-backend,example'),
    
    # Oracle Cloud Infrastructure Logging configuration
    'OCI_CONFIG_FILE': os.getenv('OCI_CONFIG_FILE'),
    'OCI_CONFIG_PROFILE': os.getenv('OCI_CONFIG_PROFILE', 'DEFAULT'),
    'OCI_LOG_GROUP_ID': os.getenv('OCI_LOG_GROUP_ID'),
    'OCI_LOG_ID': os.getenv('OCI_LOG_ID'),
    'OCI_COMPARTMENT_ID': os.getenv('OCI_COMPARTMENT_ID'),
    'OCI_SOURCE': os.getenv('OCI_SOURCE', 'FlaskMultiBackendLogs'),
    'OCI_LOG_LEVEL': os.getenv('OCI_LOG_LEVEL', 'INFO'),
    'OCI_ENVIRONMENT': os.getenv('OCI_ENVIRONMENT', 'development'),
})

def get_current_user():
    """
    Mock function to simulate getting current user information.
    In a real application, this would integrate with your authentication system.
    """
    users = [
        {"id": 1, "username": "alice", "email": "alice@example.com"},
        {"id": 2, "username": "bob", "email": "bob@example.com"},
        {"id": 3, "username": "charlie", "email": "charlie@example.com"},
    ]
    return random.choice(users)

# Initialize all logging extensions
graylog = GraylogExtension(app, get_current_user=get_current_user)
gcp_log = GCPLogExtension(app, get_current_user=get_current_user)
aws_log = AWSLogExtension(app, get_current_user=get_current_user)
azure_log = AzureLogExtension(app, get_current_user=get_current_user)
ibm_log = IBMLogExtension(app, get_current_user=get_current_user)
oci_log = OCILogExtension(app, get_current_user=get_current_user)

# Set up logging for all backends

@app.before_request
def before_request():
    """Set up request-specific data for logging context."""
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()
    
    # Log request start
    app.logger.info("Request started", extra={
        'event_type': 'request_start',
        'request_id': g.request_id,
        'method': request.method,
        'path': request.path,
        'remote_addr': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.after_request
def after_request(response):
    """Log request completion details."""
    duration = time.time() - g.start_time
    
    app.logger.info("Request completed", extra={
        'event_type': 'request_end',
        'request_id': g.request_id,
        'status_code': response.status_code,
        'duration_ms': round(duration * 1000, 2),
        'response_size': len(response.get_data()),
        'timestamp': datetime.utcnow().isoformat()
    })
    
    return response

@app.route('/')
def index():
    """Main page with information about configured logging backends."""
    app.logger.info("Index page accessed", extra={
        'endpoint': '/',
        'configured_backends': get_configured_backends()
    })
    
    return jsonify({
        'message': 'Flask Network Logging Multi-Backend Example',
        'configured_backends': get_configured_backends(),
        'endpoints': [
            '/ - This page',
            '/health - Health check',
            '/api/users - Sample API endpoint',
            '/log-levels - Demonstrate different log levels',
            '/error - Trigger an error for testing',
            '/performance - Performance monitoring example',
            '/custom-fields - Custom field logging example'
        ]
    })

@app.route('/health')
def health_check():
    """Health check endpoint."""
    app.logger.info("Health check requested", extra={
        'health_status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })
    
    return jsonify({
        'status': 'healthy',
        'service': 'flask-network-logging-multi-backend',
        'backends': get_configured_backends(),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/users')
def api_users():
    """Sample API endpoint with structured logging."""
    app.logger.info("Users API endpoint accessed", extra={
        'api_endpoint': '/api/users',
        'operation': 'list_users',
        'user_count': 3
    })
    
    users = [
        {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
        {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'},
        {'id': 3, 'name': 'Charlie', 'email': 'charlie@example.com'}
    ]
    
    return jsonify({'users': users, 'count': len(users)})

@app.route('/log-levels')
def log_levels():
    """Demonstrate different log levels across all backends."""
    request_id = g.request_id
    
    # Debug level
    app.logger.debug("Debug message example", extra={
        'log_level_demo': 'debug',
        'request_id': request_id,
        'debug_info': {'step': 1, 'component': 'log_levels_endpoint'}
    })
    
    # Info level
    app.logger.info("Info message example", extra={
        'log_level_demo': 'info',
        'request_id': request_id,
        'info_data': {'action': 'demonstrate_logging', 'level': 'info'}
    })
    
    # Warning level
    app.logger.warning("Warning message example", extra={
        'log_level_demo': 'warning',
        'request_id': request_id,
        'warning_reason': 'This is just a demonstration'
    })
    
    # Error level (without raising an exception)
    app.logger.error("Error message example", extra={
        'log_level_demo': 'error',
        'request_id': request_id,
        'error_type': 'demonstration',
        'simulated_error': True
    })
    
    return jsonify({
        'message': 'Log levels demonstrated',
        'levels_sent': ['debug', 'info', 'warning', 'error'],
        'request_id': request_id,
        'note': 'Check your configured logging backends for these messages'
    })

@app.route('/error')
def trigger_error():
    """Endpoint that triggers an actual error for testing error logging."""
    app.logger.warning("About to trigger an intentional error for testing")
    
    try:
        # Intentionally trigger an error
        result = 1 / 0
    except ZeroDivisionError as e:
        app.logger.error("Intentional error triggered for testing", extra={
            'error_type': 'ZeroDivisionError',
            'error_message': str(e),
            'intentional': True,
            'endpoint': '/error'
        })
        return jsonify({
            'error': 'Intentional error for testing',
            'message': 'Check your logging backends for error details'
        }), 500

@app.route('/performance')
def performance_monitoring():
    """Demonstrate performance monitoring with structured logging."""
    start_time = time.time()
    
    # Simulate some work
    time.sleep(random.uniform(0.1, 0.5))
    
    # Simulate database query
    db_start = time.time()
    time.sleep(random.uniform(0.05, 0.15))
    db_duration = time.time() - db_start
    
    # Simulate API call
    api_start = time.time()
    time.sleep(random.uniform(0.02, 0.08))
    api_duration = time.time() - api_start
    
    total_duration = time.time() - start_time
    
    app.logger.info("Performance metrics", extra={
        'performance_monitoring': True,
        'total_duration_ms': round(total_duration * 1000, 2),
        'db_query_duration_ms': round(db_duration * 1000, 2),
        'api_call_duration_ms': round(api_duration * 1000, 2),
        'endpoint': '/performance'
    })
    
    return jsonify({
        'message': 'Performance monitoring example',
        'metrics': {
            'total_duration_ms': round(total_duration * 1000, 2),
            'db_query_duration_ms': round(db_duration * 1000, 2),
            'api_call_duration_ms': round(api_duration * 1000, 2)
        }
    })

@app.route('/custom-fields')
def custom_fields():
    """Demonstrate logging with custom fields."""
    custom_data = {
        'business_metric': random.randint(100, 1000),
        'feature_flag': random.choice(['enabled', 'disabled']),
        'experiment_group': random.choice(['control', 'treatment_a', 'treatment_b']),
        'customer_tier': random.choice(['basic', 'premium', 'enterprise']),
        'transaction_id': str(uuid.uuid4()),
        'source_system': 'flask-example-app'
    }
    
    app.logger.info("Custom fields logging example", extra=custom_data)
    
    return jsonify({
        'message': 'Custom fields logged successfully',
        'custom_data': custom_data,
        'note': 'These custom fields will appear in all configured logging backends'
    })

def get_configured_backends():
    """Return list of configured logging backends."""
    backends = []
    
    if app.config.get('GRAYLOG_HOST'):
        backends.append('Graylog')
    if app.config.get('GCP_PROJECT_ID'):
        backends.append('Google Cloud Logging')
    if app.config.get('AWS_LOG_GROUP'):
        backends.append('AWS CloudWatch Logs')
    if app.config.get('AZURE_WORKSPACE_ID'):
        backends.append('Azure Monitor Logs')
    if app.config.get('IBM_INGESTION_KEY'):
        backends.append('IBM Cloud Logs')
    
    return backends

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors with logging."""
    app.logger.error("Internal server error occurred", extra={
        'error_type': 'internal_server_error',
        'error_message': str(error),
        'request_id': getattr(g, 'request_id', 'unknown')
    })
    
    return jsonify({
        'error': 'Internal server error',
        'request_id': getattr(g, 'request_id', 'unknown')
    }), 500

if __name__ == '__main__':
    # Display configuration information
    print("Flask Network Logging Multi-Backend Example")
    print("=" * 50)
    
    backends = get_configured_backends()
    if backends:
        print(f"Configured logging backends: {', '.join(backends)}")
    else:
        print("No remote logging backends configured - using console only")
    
    print("\nConfiguration check:")
    print(f"  Graylog: {'✓' if app.config.get('GRAYLOG_HOST') else '✗'} (Host: {app.config.get('GRAYLOG_HOST', 'Not set')})")
    print(f"  GCP: {'✓' if app.config.get('GCP_PROJECT_ID') else '✗'} (Project: {app.config.get('GCP_PROJECT_ID', 'Not set')})")
    print(f"  AWS: {'✓' if app.config.get('AWS_LOG_GROUP') else '✗'} (Log Group: {app.config.get('AWS_LOG_GROUP', 'Not set')})")
    print(f"  Azure: {'✓' if app.config.get('AZURE_WORKSPACE_ID') else '✗'} (Workspace: {app.config.get('AZURE_WORKSPACE_ID', 'Not set')})")
    
    print("\nStarting Flask app on http://localhost:5000")
    print("Available endpoints:")
    print("  / - Main page")
    print("  /health - Health check")
    print("  /api/users - Sample API")
    print("  /log-levels - Different log levels")
    print("  /error - Trigger error")
    print("  /performance - Performance monitoring")
    print("  /custom-fields - Custom field logging")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
