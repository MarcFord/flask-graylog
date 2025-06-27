#!/usr/bin/env python3
"""
IBM Cloud Logging Flask Example Application

This example demonstrates how to set up a Flask application that sends logs
to IBM Cloud Logging (LogDNA). Perfect for applications running in IBM Cloud
environments like Cloud Foundry, Kubernetes Service, or Virtual Servers.

To run this example:
1. Create an IBM Cloud Logging instance
2. Get the ingestion key and endpoint
3. Configure environment variables (see .env file)
4. Install dependencies: pip install flask-network-logging[ibm]
5. Run: python app.py
6. Visit http://localhost:5000

Environment Variables (see .env file):
- IBM_INGESTION_KEY: LogDNA ingestion key
- IBM_LOG_ENDPOINT: LogDNA endpoint URL
- IBM_LOG_LEVEL: Log level (default: INFO)
- IBM_ENVIRONMENT: Environment name (default: development)
"""

import os
import sys
from flask import Flask, request, jsonify, g
import time
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from flask_remote_logging import IBMLogExtension

app = Flask(__name__)

# Configure IBM Cloud Logging
app.config.update({
    'IBM_INGESTION_KEY': os.getenv('IBM_INGESTION_KEY', 'your-ingestion-key'),
    'IBM_LOG_ENDPOINT': os.getenv('IBM_LOG_ENDPOINT', 'logs.us-south.logging.cloud.ibm.com'),
    'IBM_LOG_LEVEL': os.getenv('IBM_LOG_LEVEL', 'INFO'),
    'IBM_ENVIRONMENT': os.getenv('IBM_ENVIRONMENT', 'development'),
    'IBM_APP_NAME': os.getenv('IBM_APP_NAME', 'flask-ibm-example'),
    'IBM_HOSTNAME': os.getenv('IBM_HOSTNAME', 'localhost'),
})

def get_current_user():
    """
    Example function to get current user information.
    In IBM Cloud environments, this might integrate with App ID, IAM, or other auth services.
    """
    return {
        'id': request.headers.get('X-User-ID', 'anonymous'),
        'username': request.headers.get('X-Username', 'guest'),
        'email': request.headers.get('X-User-Email', 'guest@example.com'),
        'ibm_user_id': request.headers.get('X-IBM-User-ID', 'guest@example.com'),
        'iam_subject': request.headers.get('X-IBM-Subject', 'unknown')
    }

# Initialize IBM Cloud Logging extension
ibm_log = IBMLogExtension(app, get_current_user=get_current_user)

@app.before_request
def before_request():
    """Log request start and set up request timing."""
    g.start_time = time.time()
    g.request_id = str(uuid.uuid4())
    
    app.logger.info("Request started", extra={
        'request_id': g.request_id,
        'method': request.method,
        'url': request.url,
        'endpoint': request.endpoint,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'ibm_request_id': request.headers.get('X-Request-ID', 'local'),
        'ibm_correlation_id': request.headers.get('X-Correlation-ID', 'local'),
    })

@app.after_request
def after_request(response):
    """Log request completion."""
    duration = time.time() - g.start_time
    
    app.logger.info("Request completed", extra={
        'request_id': g.request_id,
        'status_code': response.status_code,
        'duration_ms': round(duration * 1000, 2),
        'content_length': response.content_length,
        'ibm_endpoint': app.config.get('IBM_LOG_ENDPOINT'),
    })
    
    return response

@app.route('/')
def index():
    """Home page with API information."""
    app.logger.info("Home page accessed", extra={
        'endpoint': 'index',
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'ibm_info': {
            'endpoint': app.config.get('IBM_LOG_ENDPOINT'),
            'app_name': app.config.get('IBM_APP_NAME'),
        }
    })
    
    return jsonify({
        'message': 'IBM Cloud Logging Flask Example',
        'status': 'running',
        'logging_backend': 'IBM Cloud Logging (LogDNA)',
        'endpoints': {
            '/': 'This page',
            '/health': 'Health check',
            '/users': 'Mock users API',
            '/logs/test': 'Test different log levels',
            '/logs/user-context': 'Test user context logging',
            '/logs/error': 'Test error logging',
            '/logs/ibm-metrics': 'Test IBM-specific metrics',
            '/logs/performance': 'Test performance logging'
        },
        'ibm_config': {
            'endpoint': app.config.get('IBM_LOG_ENDPOINT'),
            'app_name': app.config.get('IBM_APP_NAME'),
            'environment': app.config.get('IBM_ENVIRONMENT')
        }
    })

@app.route('/health')
def health():
    """Health check endpoint with IBM metadata."""
    app.logger.info("Health check requested", extra={
        'endpoint': 'health',
        'check_type': 'ibm_health',
        'ibm_metadata': {
            'endpoint': app.config.get('IBM_LOG_ENDPOINT'),
            'service': 'flask-app',
            'app_name': app.config.get('IBM_APP_NAME'),
            'hostname': app.config.get('IBM_HOSTNAME')
        }
    })
    
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'flask-ibm-logging-example',
        'ibm_endpoint': app.config.get('IBM_LOG_ENDPOINT')
    })

@app.route('/users')
def users():
    """Mock users endpoint with structured logging."""
    users_data = [
        {'id': 1, 'name': 'Alice IBM', 'role': 'admin'},
        {'id': 2, 'name': 'Bob Watson', 'role': 'user'},
        {'id': 3, 'name': 'Charlie Cloud', 'role': 'viewer'}
    ]
    
    app.logger.info("Users endpoint accessed", extra={
        'endpoint': 'users',
        'total_users': len(users_data),
        'operation': 'list_users',
        'ibm_service': 'user-service'
    })
    
    return jsonify({
        'users': users_data,
        'total': len(users_data),
        'source': 'ibm_example'
    })

@app.route('/logs/test')
def test_logs():
    """Test different log levels."""
    app.logger.debug("Debug log from IBM example", extra={'log_type': 'debug_test'})
    app.logger.info("Info log from IBM example", extra={'log_type': 'info_test'})
    app.logger.warning("Warning log from IBM example", extra={'log_type': 'warning_test'})
    app.logger.error("Error log from IBM example", extra={'log_type': 'error_test'})
    
    return jsonify({
        'message': 'Various log levels sent to IBM Cloud Logging',
        'levels_tested': ['debug', 'info', 'warning', 'error']
    })

@app.route('/logs/user-context')
def test_user_context():
    """Test user context logging."""
    user = get_current_user()
    
    app.logger.info("User context logging test", extra={
        'user_context': user,
        'operation': 'user_context_test',
        'ibm_resource': 'user-service'
    })
    
    return jsonify({
        'message': 'User context logged to IBM Cloud Logging',
        'user': user
    })

@app.route('/logs/error')
def test_error():
    """Test error logging and exception handling."""
    try:
        # Intentionally cause an error
        result = 1 / 0
    except ZeroDivisionError as e:
        app.logger.error("Division by zero error occurred", extra={
            'error_type': 'ZeroDivisionError',
            'error_message': str(e),
            'endpoint': 'test_error',
            'severity': 'ERROR',
            'ibm_error_tracking': True
        }, exc_info=True)
        
        return jsonify({
            'error': 'Division by zero',
            'message': 'Error logged to IBM Cloud Logging',
            'logged': True
        }), 500

@app.route('/logs/ibm-metrics')
def test_ibm_metrics():
    """Test IBM-specific metrics and structured logging."""
    metrics = {
        'cpu_usage': 38.9,
        'memory_usage': 74.6,
        'disk_usage': 35.2,
        'network_io': 189.7
    }
    
    app.logger.info("IBM metrics collected", extra={
        'metrics': metrics,
        'metric_type': 'system_performance',
        'ibm_resource': {
            'type': 'virtual_server',
            'region': 'us-south',
            'datacenter': 'dal10'
        },
        'timestamp': time.time()
    })
    
    return jsonify({
        'message': 'IBM metrics logged to Cloud Logging',
        'metrics': metrics
    })

@app.route('/logs/performance')
def test_performance():
    """Test performance logging with timing."""
    start_time = time.time()
    
    # Simulate some work
    time.sleep(0.1)
    
    processing_time = time.time() - start_time
    
    app.logger.info("Performance test completed", extra={
        'performance': {
            'processing_time_ms': round(processing_time * 1000, 2),
            'operation': 'performance_test',
            'status': 'success'
        },
        'ibm_monitoring': {
            'metric_type': 'response_time',
            'value': round(processing_time * 1000, 2),
            'unit': 'milliseconds',
            'component': 'flask-app'
        }
    })
    
    return jsonify({
        'message': 'Performance metrics logged to IBM Cloud Logging',
        'processing_time_ms': round(processing_time * 1000, 2)
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with logging."""
    app.logger.warning("Page not found", extra={
        'error_type': '404_not_found',
        'requested_url': request.url,
        'method': request.method,
        'user_agent': request.headers.get('User-Agent'),
        'ibm_error_context': 'page_not_found'
    })
    
    return jsonify({
        'error': 'Page not found',
        'requested_url': request.url
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with logging."""
    app.logger.error("Internal server error", extra={
        'error_type': '500_internal_error',
        'error_message': str(error),
        'requested_url': request.url,
        'method': request.method,
        'ibm_error_tracking': True
    }, exc_info=True)
    
    return jsonify({
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.logger.info("Starting IBM Flask logging example", extra={
        'startup': True,
        'ibm_config': {
            'endpoint': app.config.get('IBM_LOG_ENDPOINT'),
            'app_name': app.config.get('IBM_APP_NAME'),
            'environment': app.config.get('IBM_ENVIRONMENT')
        }
    })
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config.get('IBM_ENVIRONMENT') == 'development'
    )
