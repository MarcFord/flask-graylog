#!/usr/bin/env python3
"""
Google Cloud Logging Flask Example Application

This example demonstrates how to set up a Flask application that sends logs
to Google Cloud Logging. Perfect for applications running in Google Cloud
environments like Compute Engine, App Engine, Cloud Run, or GKE.

To run this example:
1. Set up a Google Cloud Project
2. Create a service account with Logging permissions (or use default credentials)
3. Configure environment variables (see .env file)
4. Install dependencies: pip install flask-network-logging[gcp]
5. Run: python app.py
6. Visit http://localhost:5000

Environment Variables (see .env file):
- GCP_PROJECT_ID: Google Cloud project ID
- GCP_CREDENTIALS_PATH: Path to service account JSON file (optional)
- GCP_LOG_NAME: Cloud Logging log name
- GCP_LOG_LEVEL: Log level (default: INFO)
- GCP_ENVIRONMENT: Environment name (default: development)
"""

import os
import sys
from flask import Flask, request, jsonify, g
import time
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from flask_remote_logging import GCPLogExtension

app = Flask(__name__)

# Configure Google Cloud Logging
app.config.update({
    'GCP_PROJECT_ID': os.getenv('GCP_PROJECT_ID', 'your-gcp-project-id'),
    'GCP_CREDENTIALS_PATH': os.getenv('GCP_CREDENTIALS_PATH'),
    'GCP_LOG_NAME': os.getenv('GCP_LOG_NAME', 'flask-gcp-example'),
    'GCP_LOG_LEVEL': os.getenv('GCP_LOG_LEVEL', 'INFO'),
    'GCP_ENVIRONMENT': os.getenv('GCP_ENVIRONMENT', 'development'),
    'GCP_LABELS': {
        'service': 'flask-app',
        'version': '1.0.0',
    }
})

def get_current_user():
    """
    Example function to get current user information.
    In GCP environments, this might integrate with Identity Platform, IAM, or other auth services.
    """
    return {
        'id': request.headers.get('X-User-ID', 'anonymous'),
        'username': request.headers.get('X-Username', 'guest'),
        'email': request.headers.get('X-User-Email', 'guest@example.com'),
        'gcp_user_email': request.headers.get('X-GCP-User-Email', 'guest@example.com')
    }

# Initialize Google Cloud Logging extension
gcp_log = GCPLogExtension(app, get_current_user=get_current_user)

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
        'gcp_trace_id': request.headers.get('X-Cloud-Trace-Context', 'local'),
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
        'gcp_project': app.config.get('GCP_PROJECT_ID'),
    })
    
    return response

@app.route('/')
def index():
    """Home page with API information."""
    app.logger.info("Home page accessed", extra={
        'endpoint': 'index',
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'gcp_info': {
            'project_id': app.config.get('GCP_PROJECT_ID'),
            'log_name': app.config.get('GCP_LOG_NAME'),
        }
    })
    
    return jsonify({
        'message': 'Google Cloud Logging Flask Example',
        'status': 'running',
        'logging_backend': 'Google Cloud Logging',
        'endpoints': {
            '/': 'This page',
            '/health': 'Health check',
            '/users': 'Mock users API',
            '/logs/test': 'Test different log levels',
            '/logs/user-context': 'Test user context logging',
            '/logs/error': 'Test error logging',
            '/logs/gcp-metrics': 'Test GCP-specific metrics',
            '/logs/performance': 'Test performance logging'
        },
        'gcp_config': {
            'project_id': app.config.get('GCP_PROJECT_ID'),
            'log_name': app.config.get('GCP_LOG_NAME'),
            'environment': app.config.get('GCP_ENVIRONMENT')
        }
    })

@app.route('/health')
def health():
    """Health check endpoint with GCP metadata."""
    app.logger.info("Health check requested", extra={
        'endpoint': 'health',
        'check_type': 'gcp_health',
        'gcp_metadata': {
            'project_id': app.config.get('GCP_PROJECT_ID'),
            'service': 'flask-app',
            'log_name': app.config.get('GCP_LOG_NAME')
        }
    })
    
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'flask-gcp-logging-example',
        'gcp_project': app.config.get('GCP_PROJECT_ID')
    })

@app.route('/users')
def users():
    """Mock users endpoint with structured logging."""
    users_data = [
        {'id': 1, 'name': 'Alice GCP', 'role': 'admin'},
        {'id': 2, 'name': 'Bob Cloud', 'role': 'user'},
        {'id': 3, 'name': 'Charlie Logging', 'role': 'viewer'}
    ]
    
    app.logger.info("Users endpoint accessed", extra={
        'endpoint': 'users',
        'total_users': len(users_data),
        'operation': 'list_users',
        'gcp_service': 'user-service'
    })
    
    return jsonify({
        'users': users_data,
        'total': len(users_data),
        'source': 'gcp_example'
    })

@app.route('/logs/test')
def test_logs():
    """Test different log levels."""
    app.logger.debug("Debug log from GCP example", extra={'log_type': 'debug_test'})
    app.logger.info("Info log from GCP example", extra={'log_type': 'info_test'})
    app.logger.warning("Warning log from GCP example", extra={'log_type': 'warning_test'})
    app.logger.error("Error log from GCP example", extra={'log_type': 'error_test'})
    
    return jsonify({
        'message': 'Various log levels sent to Google Cloud Logging',
        'levels_tested': ['debug', 'info', 'warning', 'error']
    })

@app.route('/logs/user-context')
def test_user_context():
    """Test user context logging."""
    user = get_current_user()
    
    app.logger.info("User context logging test", extra={
        'user_context': user,
        'operation': 'user_context_test',
        'gcp_resource': 'user-service'
    })
    
    return jsonify({
        'message': 'User context logged to Google Cloud Logging',
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
            'gcp_error_reporting': True
        }, exc_info=True)
        
        return jsonify({
            'error': 'Division by zero',
            'message': 'Error logged to Google Cloud Logging',
            'logged': True
        }), 500

@app.route('/logs/gcp-metrics')
def test_gcp_metrics():
    """Test GCP-specific metrics and structured logging."""
    metrics = {
        'cpu_usage': 45.2,
        'memory_usage': 78.1,
        'disk_usage': 32.5,
        'network_io': 123.4
    }
    
    app.logger.info("GCP metrics collected", extra={
        'metrics': metrics,
        'metric_type': 'system_performance',
        'gcp_resource': {
            'type': 'gce_instance',
            'labels': {
                'instance_id': 'gcp-instance-123',
                'zone': 'us-central1-a'
            }
        },
        'timestamp': time.time()
    })
    
    return jsonify({
        'message': 'GCP metrics logged to Cloud Logging',
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
        'gcp_monitoring': {
            'metric_kind': 'GAUGE',
            'value_type': 'DOUBLE',
            'unit': 'ms'
        }
    })
    
    return jsonify({
        'message': 'Performance metrics logged to Google Cloud Logging',
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
        'gcp_error_context': 'page_not_found'
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
        'gcp_error_reporting': True
    }, exc_info=True)
    
    return jsonify({
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.logger.info("Starting GCP Flask logging example", extra={
        'startup': True,
        'gcp_config': {
            'project_id': app.config.get('GCP_PROJECT_ID'),
            'log_name': app.config.get('GCP_LOG_NAME'),
            'environment': app.config.get('GCP_ENVIRONMENT')
        }
    })
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config.get('GCP_ENVIRONMENT') == 'development'
    )
