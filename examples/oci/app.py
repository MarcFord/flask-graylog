#!/usr/bin/env python3
"""
Oracle Cloud Infrastructure (OCI) Logging Flask Example Application

This example demonstrates how to set up a Flask application that sends logs
to OCI Logging service. Perfect for applications running in Oracle Cloud
environments like Compute instances, Container Engine, or Functions.

To run this example:
1. Set up OCI configuration and credentials
2. Create an OCI Log Group and Log
3. Configure environment variables (see .env file)
4. Install dependencies: pip install flask-network-logging[oci]
5. Run: python app.py
6. Visit http://localhost:5000

Environment Variables (see .env file):
- OCI_CONFIG_FILE: Path to OCI config file
- OCI_CONFIG_PROFILE: OCI config profile name
- OCI_LOG_GROUP_ID: OCI Log Group OCID
- OCI_LOG_ID: OCI Log OCID
- OCI_LOG_LEVEL: Log level (default: INFO)
- OCI_ENVIRONMENT: Environment name (default: development)
"""

import os
import sys
from flask import Flask, request, jsonify, g
import time
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from flask_remote_logging import OCILogExtension

app = Flask(__name__)

# Configure OCI Logging
app.config.update({
    'OCI_CONFIG_FILE': os.getenv('OCI_CONFIG_FILE', '~/.oci/config'),
    'OCI_CONFIG_PROFILE': os.getenv('OCI_CONFIG_PROFILE', 'DEFAULT'),
    'OCI_LOG_GROUP_ID': os.getenv('OCI_LOG_GROUP_ID', 'ocid1.loggroup.oc1..your-log-group-id'),
    'OCI_LOG_ID': os.getenv('OCI_LOG_ID', 'ocid1.log.oc1..your-log-id'),
    'OCI_LOG_LEVEL': os.getenv('OCI_LOG_LEVEL', 'INFO'),
    'OCI_ENVIRONMENT': os.getenv('OCI_ENVIRONMENT', 'development'),
    'OCI_COMPARTMENT_ID': os.getenv('OCI_COMPARTMENT_ID', 'ocid1.compartment.oc1..your-compartment-id'),
    'OCI_LOG_SOURCE_NAME': os.getenv('OCI_LOG_SOURCE_NAME', 'flask-oci-example'),
})

def get_current_user():
    """
    Example function to get current user information.
    In OCI environments, this might integrate with Identity and Access Management (IAM) or other auth services.
    """
    return {
        'id': request.headers.get('X-User-ID', 'anonymous'),
        'username': request.headers.get('X-Username', 'guest'),
        'email': request.headers.get('X-User-Email', 'guest@example.com'),
        'oci_user_ocid': request.headers.get('X-OCI-User-OCID', 'ocid1.user.oc1..guest'),
        'oci_tenancy_ocid': request.headers.get('X-OCI-Tenancy-OCID', 'ocid1.tenancy.oc1..unknown')
    }

# Initialize OCI Logging extension
oci_log = OCILogExtension(app, get_current_user=get_current_user)

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
        'oci_request_id': request.headers.get('X-OCI-Request-Id', 'local'),
        'oci_trace_id': request.headers.get('X-OCI-Trace-Id', 'local'),
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
        'oci_log_group': app.config.get('OCI_LOG_GROUP_ID'),
    })
    
    return response

@app.route('/')
def index():
    """Home page with API information."""
    app.logger.info("Home page accessed", extra={
        'endpoint': 'index',
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'oci_info': {
            'log_group_id': app.config.get('OCI_LOG_GROUP_ID'),
            'log_id': app.config.get('OCI_LOG_ID'),
            'source_name': app.config.get('OCI_LOG_SOURCE_NAME'),
        }
    })
    
    return jsonify({
        'message': 'Oracle Cloud Infrastructure Logging Flask Example',
        'status': 'running',
        'logging_backend': 'OCI Logging',
        'endpoints': {
            '/': 'This page',
            '/health': 'Health check',
            '/users': 'Mock users API',
            '/logs/test': 'Test different log levels',
            '/logs/user-context': 'Test user context logging',
            '/logs/error': 'Test error logging',
            '/logs/oci-metrics': 'Test OCI-specific metrics',
            '/logs/performance': 'Test performance logging'
        },
        'oci_config': {
            'log_group_id': app.config.get('OCI_LOG_GROUP_ID'),
            'log_id': app.config.get('OCI_LOG_ID'),
            'source_name': app.config.get('OCI_LOG_SOURCE_NAME'),
            'environment': app.config.get('OCI_ENVIRONMENT')
        }
    })

@app.route('/health')
def health():
    """Health check endpoint with OCI metadata."""
    app.logger.info("Health check requested", extra={
        'endpoint': 'health',
        'check_type': 'oci_health',
        'oci_metadata': {
            'log_group_id': app.config.get('OCI_LOG_GROUP_ID'),
            'log_id': app.config.get('OCI_LOG_ID'),
            'service': 'flask-app',
            'source_name': app.config.get('OCI_LOG_SOURCE_NAME'),
            'compartment_id': app.config.get('OCI_COMPARTMENT_ID')
        }
    })
    
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'flask-oci-logging-example',
        'oci_log_group': app.config.get('OCI_LOG_GROUP_ID')
    })

@app.route('/users')
def users():
    """Mock users endpoint with structured logging."""
    users_data = [
        {'id': 1, 'name': 'Alice Oracle', 'role': 'admin'},
        {'id': 2, 'name': 'Bob Cloud', 'role': 'user'},
        {'id': 3, 'name': 'Charlie Infrastructure', 'role': 'viewer'}
    ]
    
    app.logger.info("Users endpoint accessed", extra={
        'endpoint': 'users',
        'total_users': len(users_data),
        'operation': 'list_users',
        'oci_service': 'user-service'
    })
    
    return jsonify({
        'users': users_data,
        'total': len(users_data),
        'source': 'oci_example'
    })

@app.route('/logs/test')
def test_logs():
    """Test different log levels."""
    app.logger.debug("Debug log from OCI example", extra={'log_type': 'debug_test'})
    app.logger.info("Info log from OCI example", extra={'log_type': 'info_test'})
    app.logger.warning("Warning log from OCI example", extra={'log_type': 'warning_test'})
    app.logger.error("Error log from OCI example", extra={'log_type': 'error_test'})
    
    return jsonify({
        'message': 'Various log levels sent to OCI Logging',
        'levels_tested': ['debug', 'info', 'warning', 'error']
    })

@app.route('/logs/user-context')
def test_user_context():
    """Test user context logging."""
    user = get_current_user()
    
    app.logger.info("User context logging test", extra={
        'user_context': user,
        'operation': 'user_context_test',
        'oci_resource': 'user-service'
    })
    
    return jsonify({
        'message': 'User context logged to OCI Logging',
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
            'oci_error_tracking': True
        }, exc_info=True)
        
        return jsonify({
            'error': 'Division by zero',
            'message': 'Error logged to OCI Logging',
            'logged': True
        }), 500

@app.route('/logs/oci-metrics')
def test_oci_metrics():
    """Test OCI-specific metrics and structured logging."""
    metrics = {
        'cpu_usage': 41.7,
        'memory_usage': 68.9,
        'disk_usage': 29.3,
        'network_io': 203.5
    }
    
    app.logger.info("OCI metrics collected", extra={
        'metrics': metrics,
        'metric_type': 'system_performance',
        'oci_resource': {
            'type': 'compute_instance',
            'compartment_id': app.config.get('OCI_COMPARTMENT_ID'),
            'availability_domain': 'AD-1',
            'region': 'us-ashburn-1'
        },
        'timestamp': time.time()
    })
    
    return jsonify({
        'message': 'OCI metrics logged to Logging service',
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
        'oci_monitoring': {
            'metric_namespace': 'flask_app',
            'metric_name': 'response_time',
            'value': round(processing_time * 1000, 2),
            'unit': 'milliseconds',
            'dimensions': {
                'service': 'flask-app',
                'endpoint': 'performance'
            }
        }
    })
    
    return jsonify({
        'message': 'Performance metrics logged to OCI Logging',
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
        'oci_error_context': 'page_not_found'
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
        'oci_error_tracking': True
    }, exc_info=True)
    
    return jsonify({
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.logger.info("Starting OCI Flask logging example", extra={
        'startup': True,
        'oci_config': {
            'log_group_id': app.config.get('OCI_LOG_GROUP_ID'),
            'log_id': app.config.get('OCI_LOG_ID'),
            'source_name': app.config.get('OCI_LOG_SOURCE_NAME'),
            'environment': app.config.get('OCI_ENVIRONMENT')
        }
    })
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config.get('OCI_ENVIRONMENT') == 'development'
    )
