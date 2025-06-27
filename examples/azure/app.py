#!/usr/bin/env python3
"""
Azure Monitor Logs Flask Example Application

This example demonstrates how to set up a Flask application that sends logs
to Azure Monitor Logs (Log Analytics). Perfect for applications running in Azure
environments like App Service, Virtual Machines, Container Instances, or AKS.

To run this example:
1. Create an Azure Log Analytics workspace
2. Get the workspace ID and primary key
3. Configure environment variables (see .env file)
4. Install dependencies: pip install flask-network-logging[azure]
5. Run: python app.py
6. Visit http://localhost:5000

Environment Variables (see .env file):
- AZURE_WORKSPACE_ID: Log Analytics workspace ID
- AZURE_WORKSPACE_KEY: Log Analytics primary key
- AZURE_LOG_TYPE: Custom log type name
- AZURE_LOG_LEVEL: Log level (default: INFO)
- AZURE_ENVIRONMENT: Environment name (default: development)
"""

import os
import sys
from flask import Flask, request, jsonify, g
import time
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from flask_remote_logging import AzureLogExtension

app = Flask(__name__)

# Configure Azure Monitor Logs
app.config.update({
    'AZURE_WORKSPACE_ID': os.getenv('AZURE_WORKSPACE_ID', 'your-workspace-id'),
    'AZURE_WORKSPACE_KEY': os.getenv('AZURE_WORKSPACE_KEY', 'your-workspace-key'),
    'AZURE_LOG_TYPE': os.getenv('AZURE_LOG_TYPE', 'FlaskAppLogs'),
    'AZURE_LOG_LEVEL': os.getenv('AZURE_LOG_LEVEL', 'INFO'),
    'AZURE_ENVIRONMENT': os.getenv('AZURE_ENVIRONMENT', 'development'),
    'AZURE_RESOURCE_ID': os.getenv('AZURE_RESOURCE_ID', '/subscriptions/your-sub/resourceGroups/your-rg/providers/Microsoft.Web/sites/your-app'),
})

def get_current_user():
    """
    Example function to get current user information.
    In Azure environments, this might integrate with Azure AD, App Service Authentication, or other auth services.
    """
    return {
        'id': request.headers.get('X-User-ID', 'anonymous'),
        'username': request.headers.get('X-Username', 'guest'),
        'email': request.headers.get('X-User-Email', 'guest@example.com'),
        'azure_user_principal': request.headers.get('X-MS-CLIENT-PRINCIPAL-NAME', 'guest@example.com'),
        'azure_tenant_id': request.headers.get('X-MS-CLIENT-PRINCIPAL-ID', 'unknown')
    }

# Initialize Azure Monitor Logs extension
azure_log = AzureLogExtension(app, get_current_user=get_current_user)

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
        'azure_request_id': request.headers.get('X-MS-Request-Id', 'local'),
        'azure_correlation_id': request.headers.get('X-MS-Correlation-Id', 'local'),
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
        'azure_workspace': app.config.get('AZURE_WORKSPACE_ID'),
    })
    
    return response

@app.route('/')
def index():
    """Home page with API information."""
    app.logger.info("Home page accessed", extra={
        'endpoint': 'index',
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'azure_info': {
            'workspace_id': app.config.get('AZURE_WORKSPACE_ID'),
            'log_type': app.config.get('AZURE_LOG_TYPE'),
        }
    })
    
    return jsonify({
        'message': 'Azure Monitor Logs Flask Example',
        'status': 'running',
        'logging_backend': 'Azure Monitor Logs',
        'endpoints': {
            '/': 'This page',
            '/health': 'Health check',
            '/users': 'Mock users API',
            '/logs/test': 'Test different log levels',
            '/logs/user-context': 'Test user context logging',
            '/logs/error': 'Test error logging',
            '/logs/azure-metrics': 'Test Azure-specific metrics',
            '/logs/performance': 'Test performance logging'
        },
        'azure_config': {
            'workspace_id': app.config.get('AZURE_WORKSPACE_ID'),
            'log_type': app.config.get('AZURE_LOG_TYPE'),
            'environment': app.config.get('AZURE_ENVIRONMENT')
        }
    })

@app.route('/health')
def health():
    """Health check endpoint with Azure metadata."""
    app.logger.info("Health check requested", extra={
        'endpoint': 'health',
        'check_type': 'azure_health',
        'azure_metadata': {
            'workspace_id': app.config.get('AZURE_WORKSPACE_ID'),
            'service': 'flask-app',
            'log_type': app.config.get('AZURE_LOG_TYPE'),
            'resource_id': app.config.get('AZURE_RESOURCE_ID')
        }
    })
    
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'flask-azure-logging-example',
        'azure_workspace': app.config.get('AZURE_WORKSPACE_ID')
    })

@app.route('/users')
def users():
    """Mock users endpoint with structured logging."""
    users_data = [
        {'id': 1, 'name': 'Alice Azure', 'role': 'admin'},
        {'id': 2, 'name': 'Bob Monitor', 'role': 'user'},
        {'id': 3, 'name': 'Charlie Analytics', 'role': 'viewer'}
    ]
    
    app.logger.info("Users endpoint accessed", extra={
        'endpoint': 'users',
        'total_users': len(users_data),
        'operation': 'list_users',
        'azure_service': 'user-service'
    })
    
    return jsonify({
        'users': users_data,
        'total': len(users_data),
        'source': 'azure_example'
    })

@app.route('/logs/test')
def test_logs():
    """Test different log levels."""
    app.logger.debug("Debug log from Azure example", extra={'log_type': 'debug_test'})
    app.logger.info("Info log from Azure example", extra={'log_type': 'info_test'})
    app.logger.warning("Warning log from Azure example", extra={'log_type': 'warning_test'})
    app.logger.error("Error log from Azure example", extra={'log_type': 'error_test'})
    
    return jsonify({
        'message': 'Various log levels sent to Azure Monitor Logs',
        'levels_tested': ['debug', 'info', 'warning', 'error']
    })

@app.route('/logs/user-context')
def test_user_context():
    """Test user context logging."""
    user = get_current_user()
    
    app.logger.info("User context logging test", extra={
        'user_context': user,
        'operation': 'user_context_test',
        'azure_resource': 'user-service'
    })
    
    return jsonify({
        'message': 'User context logged to Azure Monitor Logs',
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
            'azure_application_insights': True
        }, exc_info=True)
        
        return jsonify({
            'error': 'Division by zero',
            'message': 'Error logged to Azure Monitor Logs',
            'logged': True
        }), 500

@app.route('/logs/azure-metrics')
def test_azure_metrics():
    """Test Azure-specific metrics and structured logging."""
    metrics = {
        'cpu_usage': 42.8,
        'memory_usage': 81.3,
        'disk_usage': 28.7,
        'network_io': 156.2
    }
    
    app.logger.info("Azure metrics collected", extra={
        'metrics': metrics,
        'metric_type': 'system_performance',
        'azure_resource': {
            'type': 'Microsoft.Web/sites',
            'id': app.config.get('AZURE_RESOURCE_ID'),
            'location': 'East US'
        },
        'timestamp': time.time()
    })
    
    return jsonify({
        'message': 'Azure metrics logged to Monitor Logs',
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
        'azure_insights': {
            'telemetry_type': 'metric',
            'metric_name': 'processing_time',
            'value': round(processing_time * 1000, 2),
            'unit': 'milliseconds'
        }
    })
    
    return jsonify({
        'message': 'Performance metrics logged to Azure Monitor Logs',
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
        'azure_error_context': 'page_not_found'
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
        'azure_application_insights': True
    }, exc_info=True)
    
    return jsonify({
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.logger.info("Starting Azure Flask logging example", extra={
        'startup': True,
        'azure_config': {
            'workspace_id': app.config.get('AZURE_WORKSPACE_ID'),
            'log_type': app.config.get('AZURE_LOG_TYPE'),
            'environment': app.config.get('AZURE_ENVIRONMENT')
        }
    })
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config.get('AZURE_ENVIRONMENT') == 'development'
    )
