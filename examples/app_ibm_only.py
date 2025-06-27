#!/usr/bin/env python3
"""
IBM Cloud Logs Only Example

This example demonstrates how to set up a Flask application that sends logs only
to IBM Cloud Logs (formerly LogDNA). This is useful when you want to 
use IBM Cloud Logs as your primary logging backend in IBM Cloud environments.

To use this example:
1. Set up your IBM Cloud Logs instance
2. Set the required environment variables (see below)
3. Run this script and visit http://localhost:5000

Required Environment Variables:
- IBM_INGESTION_KEY: Your IBM Cloud Logs ingestion key

Optional Environment Variables:
- IBM_HOSTNAME: Custom hostname (default: system hostname)
- IBM_APP_NAME: Application name (default: flask-app)
- IBM_ENV: Environment name (default: development)
- IBM_LOG_LEVEL: Logging level (default: INFO)
- IBM_ENVIRONMENT: Environment where logs should be sent (default: development)
- IBM_IP: IP address for log entries
- IBM_MAC: MAC address for log entries
- IBM_TAGS: Comma-separated list of tags
"""

import os
from flask import Flask, request, jsonify
from flask_remote_logging import IBMLogExtension

app = Flask(__name__)

# Configure IBM Cloud Logs
app.config.update({
    'IBM_INGESTION_KEY': os.getenv('IBM_INGESTION_KEY'),
    'IBM_HOSTNAME': os.getenv('IBM_HOSTNAME'),
    'IBM_APP_NAME': os.getenv('IBM_APP_NAME', 'FlaskIBMExample'),
    'IBM_ENV': os.getenv('IBM_ENV', 'development'),
    'IBM_LOG_LEVEL': os.getenv('IBM_LOG_LEVEL', 'INFO'),
    'IBM_ENVIRONMENT': os.getenv('IBM_ENVIRONMENT', 'production'),
    'IBM_IP': os.getenv('IBM_IP'),
    'IBM_MAC': os.getenv('IBM_MAC'),
    'IBM_TAGS': os.getenv('IBM_TAGS', 'flask,example,ibm-cloud'),
    'IBM_INDEX_META': os.getenv('IBM_INDEX_META', 'true').lower() == 'true',
})

# Initialize IBM Cloud Logs extension (logging setup is automatic)
ibm_log = IBMLogExtension(app)

@app.route('/')
def index():
    """Main page - demonstrates basic info logging."""
    app.logger.info("Index page accessed", extra={
        'endpoint': '/',
        'method': request.method,
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    })
    
    return jsonify({
        'message': 'IBM Cloud Logs Example App',
        'status': 'success',
        'logging_backend': 'IBM Cloud Logs',
        'ingestion_configured': bool(app.config.get('IBM_INGESTION_KEY')),
        'app_name': app.config.get('IBM_APP_NAME'),
        'endpoints': [
            '/ - This page',
            '/health - Health check',
            '/api/users - Sample API endpoint',
            '/error - Trigger an error for testing',
            '/debug - Debug level logging example',
            '/test-logs - Test different log levels'
        ]
    })

@app.route('/health')
def health_check():
    """Health check endpoint."""
    app.logger.info("Health check requested")
    return jsonify({
        'status': 'healthy', 
        'service': 'flask-ibm-logging-example',
        'logging_backend': 'IBM Cloud Logs'
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

@app.route('/error')
def trigger_error():
    """Endpoint that triggers an error for testing error logging."""
    app.logger.warning("About to trigger an intentional error for testing")
    
    try:
        # Intentionally trigger an error
        result = 1 / 0
    except ZeroDivisionError as e:
        app.logger.error("Intentional error triggered for testing", extra={
            'error_type': 'ZeroDivisionError',
            'error_message': str(e),
            'endpoint': '/error'
        })
        return jsonify({
            'error': 'Intentional error for testing',
            'message': 'Check your IBM Cloud Logs for error details'
        }), 500

@app.route('/debug')
def debug_example():
    """Endpoint demonstrating debug level logging."""
    app.logger.debug("Debug information", extra={
        'debug_data': {
            'step': 1,
            'process': 'example_debug',
            'details': 'This is debug level information'
        }
    })
    
    app.logger.info("Debug endpoint accessed successfully")
    
    return jsonify({
        'message': 'Debug logging example',
        'note': 'Debug logs may not appear unless IBM_LOG_LEVEL is set to DEBUG'
    })

@app.route('/test-logs')
def test_logs():
    """Test different log levels."""
    app.logger.debug("Debug message for IBM Cloud Logs", extra={
        'log_test': True,
        'level': 'debug'
    })
    
    app.logger.info("Info message for IBM Cloud Logs", extra={
        'log_test': True,
        'level': 'info',
        'custom_field': 'test_value'
    })
    
    app.logger.warning("Warning message for IBM Cloud Logs", extra={
        'log_test': True,
        'level': 'warning'
    })
    
    app.logger.error("Error message for IBM Cloud Logs", extra={
        'log_test': True,
        'level': 'error'
    })
    
    return jsonify({
        'message': 'Test logs sent to IBM Cloud Logs',
        'levels_tested': ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    })

@app.route('/performance')
def performance_test():
    """Endpoint for testing performance logging."""
    import time
    import random
    
    start_time = time.time()
    
    # Simulate some processing
    processing_time = random.uniform(0.1, 0.5)
    time.sleep(processing_time)
    
    end_time = time.time()
    duration = end_time - start_time
    
    app.logger.info("Performance test completed", extra={
        'performance_metrics': {
            'duration_seconds': round(duration, 3),
            'processing_time': round(processing_time, 3),
            'endpoint': '/performance'
        },
        'test_type': 'performance'
    })
    
    return jsonify({
        'message': 'Performance test completed',
        'duration_seconds': round(duration, 3),
        'note': 'Performance metrics logged to IBM Cloud Logs'
    })

if __name__ == '__main__':
    # Check if required configuration is present
    ingestion_key = app.config.get('IBM_INGESTION_KEY')
    
    if not ingestion_key:
        print("Warning: IBM Cloud Logs not fully configured.")
        print("Set IBM_INGESTION_KEY environment variable.")
        print("Logs will only be sent to console until IBM Cloud Logs is configured.")
    else:
        print(f"IBM Cloud Logs configured with ingestion key: {ingestion_key[:10]}...")
        print(f"App name: {app.config.get('IBM_APP_NAME')}")
        print(f"Environment: {app.config.get('IBM_ENV')}")
        print(f"Hostname: {app.config.get('IBM_HOSTNAME', 'system default')}")
    
    print("Starting Flask app on http://localhost:5000")
    print("Available endpoints:")
    print("  / - Main page")
    print("  /health - Health check")
    print("  /api/users - Sample API")
    print("  /error - Trigger error")
    print("  /debug - Debug logging")
    print("  /test-logs - Test all log levels")
    print("  /performance - Performance metrics")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
