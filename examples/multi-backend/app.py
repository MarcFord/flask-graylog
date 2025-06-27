#!/usr/bin/env python3
"""
Multi-Backend Logging Flask Example Application

This example demonstrates how to set up a Flask application that sends logs
to multiple cloud logging services simultaneously. This is useful for:
- Multi-cloud deployments
- Backup logging strategies
- Service migration scenarios
- Centralized log aggregation

Supported backends:
- Graylog (GELF)
- AWS CloudWatch Logs
- Google Cloud Logging
- Azure Monitor Logs
- IBM Cloud Logging (LogDNA)
- Oracle Cloud Infrastructure (OCI) Logging

To run this example:
1. Configure environment variables for the backends you want to use (see .env file)
2. Install dependencies: pip install flask-network-logging[all]
3. Run: python app.py
4. Visit http://localhost:5000

Environment Variables (see .env file):
Configure only the backends you want to use. Each backend can be enabled/disabled independently.
"""

import os
import sys
from flask import Flask, request, jsonify, g
import time
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from flask_remote_logging import GraylogExtension, AWSLogExtension, GCPLogExtension, AzureLogExtension, IBMLogExtension, OCILogExtension

app = Flask(__name__)

# Configuration for all backends
app.config.update({
    # Global configuration
    'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
    'ENVIRONMENT': os.getenv('ENVIRONMENT', 'development'),
    
    # Graylog configuration
    'GRAYLOG_HOST': os.getenv('GRAYLOG_HOST'),
    'GRAYLOG_PORT': int(os.getenv('GRAYLOG_PORT', 12201)),
    'GRAYLOG_ENABLE': os.getenv('GRAYLOG_ENABLE', 'false').lower() == 'true',
    
    # AWS CloudWatch configuration
    'AWS_REGION': os.getenv('AWS_REGION', 'us-east-1'),
    'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
    'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
    'AWS_LOG_GROUP': os.getenv('AWS_LOG_GROUP'),
    'AWS_LOG_STREAM': os.getenv('AWS_LOG_STREAM'),
    'AWS_ENABLE': os.getenv('AWS_ENABLE', 'false').lower() == 'true',
    
    # Google Cloud Logging configuration
    'GCP_PROJECT_ID': os.getenv('GCP_PROJECT_ID'),
    'GCP_CREDENTIALS_PATH': os.getenv('GCP_CREDENTIALS_PATH'),
    'GCP_LOG_NAME': os.getenv('GCP_LOG_NAME', 'flask-multi-backend'),
    'GCP_ENABLE': os.getenv('GCP_ENABLE', 'false').lower() == 'true',
    
    # Azure Monitor Logs configuration
    'AZURE_WORKSPACE_ID': os.getenv('AZURE_WORKSPACE_ID'),
    'AZURE_WORKSPACE_KEY': os.getenv('AZURE_WORKSPACE_KEY'),
    'AZURE_LOG_TYPE': os.getenv('AZURE_LOG_TYPE', 'FlaskMultiBackend'),
    'AZURE_ENABLE': os.getenv('AZURE_ENABLE', 'false').lower() == 'true',
    
    # IBM Cloud Logging configuration
    'IBM_INGESTION_KEY': os.getenv('IBM_INGESTION_KEY'),
    'IBM_LOG_ENDPOINT': os.getenv('IBM_LOG_ENDPOINT', 'logs.us-south.logging.cloud.ibm.com'),
    'IBM_APP_NAME': os.getenv('IBM_APP_NAME', 'flask-multi-backend'),
    'IBM_ENABLE': os.getenv('IBM_ENABLE', 'false').lower() == 'true',
    
    # OCI Logging configuration
    'OCI_CONFIG_FILE': os.getenv('OCI_CONFIG_FILE', '~/.oci/config'),
    'OCI_CONFIG_PROFILE': os.getenv('OCI_CONFIG_PROFILE', 'DEFAULT'),
    'OCI_LOG_GROUP_ID': os.getenv('OCI_LOG_GROUP_ID'),
    'OCI_LOG_ID': os.getenv('OCI_LOG_ID'),
    'OCI_LOG_SOURCE_NAME': os.getenv('OCI_LOG_SOURCE_NAME', 'flask-multi-backend'),
    'OCI_ENABLE': os.getenv('OCI_ENABLE', 'false').lower() == 'true',
})

def get_current_user():
    """
    Example function to get current user information.
    This works across all cloud providers and includes provider-specific fields.
    """
    return {
        'id': request.headers.get('X-User-ID', 'anonymous'),
        'username': request.headers.get('X-Username', 'guest'),
        'email': request.headers.get('X-User-Email', 'guest@example.com'),
        'session_id': request.headers.get('X-Session-ID', 'no-session'),
        # Provider-specific user identifiers
        'aws_user_arn': request.headers.get('X-AWS-User-ARN'),
        'gcp_user_email': request.headers.get('X-GCP-User-Email'),
        'azure_user_principal': request.headers.get('X-MS-CLIENT-PRINCIPAL-NAME'),
        'ibm_user_id': request.headers.get('X-IBM-User-ID'),
        'oci_user_ocid': request.headers.get('X-OCI-User-OCID'),
    }

# Initialize enabled backends
enabled_backends = []
backend_status = {}

# Graylog
if app.config.get('GRAYLOG_ENABLE') and app.config.get('GRAYLOG_HOST'):
    try:
        graylog = GraylogExtension(app, get_current_user=get_current_user)

        enabled_backends.append('Graylog')
        backend_status['graylog'] = {'enabled': True, 'status': 'configured'}
    except Exception as e:
        backend_status['graylog'] = {'enabled': False, 'error': str(e)}

# AWS CloudWatch
if app.config.get('AWS_ENABLE') and app.config.get('AWS_LOG_GROUP'):
    try:
        aws_log = AWSLogExtension(app, get_current_user=get_current_user)

        enabled_backends.append('AWS CloudWatch')
        backend_status['aws'] = {'enabled': True, 'status': 'configured'}
    except Exception as e:
        backend_status['aws'] = {'enabled': False, 'error': str(e)}

# Google Cloud Logging
if app.config.get('GCP_ENABLE') and app.config.get('GCP_PROJECT_ID'):
    try:
        gcp_log = GCPLogExtension(app, get_current_user=get_current_user)

        enabled_backends.append('Google Cloud Logging')
        backend_status['gcp'] = {'enabled': True, 'status': 'configured'}
    except Exception as e:
        backend_status['gcp'] = {'enabled': False, 'error': str(e)}

# Azure Monitor Logs
if app.config.get('AZURE_ENABLE') and app.config.get('AZURE_WORKSPACE_ID'):
    try:
        azure_log = AzureLogExtension(app, get_current_user=get_current_user)

        enabled_backends.append('Azure Monitor Logs')
        backend_status['azure'] = {'enabled': True, 'status': 'configured'}
    except Exception as e:
        backend_status['azure'] = {'enabled': False, 'error': str(e)}

# IBM Cloud Logging
if app.config.get('IBM_ENABLE') and app.config.get('IBM_INGESTION_KEY'):
    try:
        ibm_log = IBMLogExtension(app, get_current_user=get_current_user)

        enabled_backends.append('IBM Cloud Logging')
        backend_status['ibm'] = {'enabled': True, 'status': 'configured'}
    except Exception as e:
        backend_status['ibm'] = {'enabled': False, 'error': str(e)}

# OCI Logging
if app.config.get('OCI_ENABLE') and app.config.get('OCI_LOG_GROUP_ID'):
    try:
        oci_log = OCILogExtension(app, get_current_user=get_current_user)

        enabled_backends.append('OCI Logging')
        backend_status['oci'] = {'enabled': True, 'status': 'configured'}
    except Exception as e:
        backend_status['oci'] = {'enabled': False, 'error': str(e)}

@app.before_request
def before_request():
    """Log request start and set up request timing."""
    g.start_time = time.time()
    g.request_id = str(uuid.uuid4())
    
    # Enhanced logging with multi-backend context
    app.logger.info("Request started", extra={
        'request_id': g.request_id,
        'method': request.method,
        'url': request.url,
        'endpoint': request.endpoint,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'multi_backend_info': {
            'enabled_backends': enabled_backends,
            'total_backends': len(enabled_backends),
        },
        # Provider-specific tracing headers
        'aws_request_id': request.headers.get('X-Amz-Request-Id'),
        'gcp_trace_id': request.headers.get('X-Cloud-Trace-Context'),
        'azure_request_id': request.headers.get('X-MS-Request-Id'),
        'ibm_request_id': request.headers.get('X-Request-ID'),
        'oci_request_id': request.headers.get('X-OCI-Request-Id'),
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
        'multi_backend_stats': {
            'backends_count': len(enabled_backends),
            'backends_list': enabled_backends,
        }
    })
    
    return response

@app.route('/')
def index():
    """Home page with API information and backend status."""
    app.logger.info("Home page accessed", extra={
        'endpoint': 'index',
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'backends_info': {
            'enabled_backends': enabled_backends,
            'backend_status': backend_status,
        }
    })
    
    return jsonify({
        'message': 'Multi-Backend Logging Flask Example',
        'status': 'running',
        'logging_backends': enabled_backends,
        'total_backends': len(enabled_backends),
        'backend_status': backend_status,
        'endpoints': {
            '/': 'This page',
            '/health': 'Health check',
            '/users': 'Mock users API',
            '/logs/test': 'Test different log levels',
            '/logs/user-context': 'Test user context logging',
            '/logs/error': 'Test error logging',
            '/logs/backend-test': 'Test backend-specific features',
            '/logs/performance': 'Test performance logging',
            '/logs/stress': 'Stress test all backends'
        },
        'configuration_tips': {
            'enabled_backends_env': 'Set *_ENABLE=true and provide credentials for each backend',
            'example': 'GRAYLOG_ENABLE=true AWS_ENABLE=true GCP_ENABLE=true'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint with all backend information."""
    app.logger.info("Health check requested", extra={
        'endpoint': 'health',
        'check_type': 'multi_backend_health',
        'backends_health': {
            backend: {'enabled': True, 'responding': True}
            for backend in enabled_backends
        }
    })
    
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'flask-multi-backend-logging-example',
        'backends': {
            'enabled': enabled_backends,
            'count': len(enabled_backends),
            'status': backend_status
        },
        'environment': app.config.get('ENVIRONMENT')
    })

@app.route('/users')
def users():
    """Mock users endpoint with structured logging."""
    users_data = [
        {'id': 1, 'name': 'Alice Multi', 'role': 'admin', 'preferred_backend': 'aws'},
        {'id': 2, 'name': 'Bob Cloud', 'role': 'user', 'preferred_backend': 'gcp'},
        {'id': 3, 'name': 'Charlie Enterprise', 'role': 'viewer', 'preferred_backend': 'azure'}
    ]
    
    app.logger.info("Users endpoint accessed", extra={
        'endpoint': 'users',
        'total_users': len(users_data),
        'operation': 'list_users',
        'backends_logging_to': enabled_backends,
        'data_classification': 'public'
    })
    
    return jsonify({
        'users': users_data,
        'total': len(users_data),
        'source': 'multi_backend_example',
        'logged_to_backends': enabled_backends
    })

@app.route('/logs/test')
def test_logs():
    """Test different log levels across all backends."""
    app.logger.debug("Debug log from multi-backend example", extra={
        'log_type': 'debug_test',
        'backends': enabled_backends
    })
    app.logger.info("Info log from multi-backend example", extra={
        'log_type': 'info_test',
        'backends': enabled_backends
    })
    app.logger.warning("Warning log from multi-backend example", extra={
        'log_type': 'warning_test',
        'backends': enabled_backends
    })
    app.logger.error("Error log from multi-backend example", extra={
        'log_type': 'error_test',
        'backends': enabled_backends
    })
    
    return jsonify({
        'message': f'Various log levels sent to {len(enabled_backends)} backend(s)',
        'levels_tested': ['debug', 'info', 'warning', 'error'],
        'backends': enabled_backends
    })

@app.route('/logs/user-context')
def test_user_context():
    """Test user context logging across all backends."""
    user = get_current_user()
    
    app.logger.info("User context logging test", extra={
        'user_context': user,
        'operation': 'user_context_test',
        'multi_backend_context': {
            'backends': enabled_backends,
            'user_tracking_across_clouds': True,
        }
    })
    
    return jsonify({
        'message': f'User context logged to {len(enabled_backends)} backend(s)',
        'user': user,
        'backends': enabled_backends
    })

@app.route('/logs/error')
def test_error():
    """Test error logging and exception handling across all backends."""
    try:
        # Intentionally cause an error
        result = 1 / 0
    except ZeroDivisionError as e:
        app.logger.error("Division by zero error occurred", extra={
            'error_type': 'ZeroDivisionError',
            'error_message': str(e),
            'endpoint': 'test_error',
            'severity': 'ERROR',
            'multi_backend_error_tracking': {
                'backends': enabled_backends,
                'correlation_ensures_tracking': True,
            }
        }, exc_info=True)
        
        return jsonify({
            'error': 'Division by zero',
            'message': f'Error logged to {len(enabled_backends)} backend(s)',
            'backends': enabled_backends,
            'logged': True
        }), 500

@app.route('/logs/backend-test')
def test_backend_specific():
    """Test backend-specific features and metadata."""
    backend_specific_data = {}
    
    # Add backend-specific context
    if 'AWS CloudWatch' in enabled_backends:
        backend_specific_data['aws'] = {
            'region': app.config.get('AWS_REGION'),
            'log_group': app.config.get('AWS_LOG_GROUP'),
            'instance_metadata': 'simulated-instance-data'
        }
    
    if 'Google Cloud Logging' in enabled_backends:
        backend_specific_data['gcp'] = {
            'project_id': app.config.get('GCP_PROJECT_ID'),
            'resource_type': 'gce_instance',
            'zone': 'us-central1-a'
        }
    
    if 'Azure Monitor Logs' in enabled_backends:
        backend_specific_data['azure'] = {
            'workspace_id': app.config.get('AZURE_WORKSPACE_ID'),
            'resource_group': 'flask-app-rg',
            'subscription_id': 'simulated-subscription'
        }
    
    if 'IBM Cloud Logging' in enabled_backends:
        backend_specific_data['ibm'] = {
            'endpoint': app.config.get('IBM_LOG_ENDPOINT'),
            'region': 'us-south',
            'service_instance': 'flask-logging-service'
        }
    
    if 'OCI Logging' in enabled_backends:
        backend_specific_data['oci'] = {
            'log_group_id': app.config.get('OCI_LOG_GROUP_ID'),
            'compartment_id': app.config.get('OCI_COMPARTMENT_ID'),
            'region': 'us-ashburn-1'
        }
    
    app.logger.info("Backend-specific test completed", extra={
        'test_type': 'backend_specific_features',
        'backend_data': backend_specific_data,
        'multi_backend_coordination': {
            'synchronized_logging': True,
            'cross_cloud_correlation': True,
        }
    })
    
    return jsonify({
        'message': f'Backend-specific features tested across {len(enabled_backends)} backend(s)',
        'backend_data': backend_specific_data,
        'backends': enabled_backends
    })

@app.route('/logs/performance')
def test_performance():
    """Test performance logging with multi-backend timing."""
    start_time = time.time()
    
    # Simulate some work
    time.sleep(0.1)
    
    processing_time = time.time() - start_time
    
    app.logger.info("Performance test completed", extra={
        'performance': {
            'processing_time_ms': round(processing_time * 1000, 2),
            'operation': 'multi_backend_performance_test',
            'status': 'success'
        },
        'multi_backend_performance': {
            'backends_count': len(enabled_backends),
            'parallel_logging': True,
            'estimated_overhead_ms': len(enabled_backends) * 2,  # Rough estimate
        }
    })
    
    return jsonify({
        'message': f'Performance metrics logged to {len(enabled_backends)} backend(s)',
        'processing_time_ms': round(processing_time * 1000, 2),
        'backends': enabled_backends,
        'performance_note': f'Logging to {len(enabled_backends)} backends simultaneously'
    })

@app.route('/logs/stress')
def stress_test():
    """Generate multiple log entries to stress test all backends."""
    start_time = time.time()
    log_count = 10
    
    for i in range(log_count):
        app.logger.info(f"Stress test log entry {i+1}", extra={
            'stress_test': {
                'entry_number': i + 1,
                'total_entries': log_count,
                'backends_count': len(enabled_backends),
            },
            'timestamp': time.time(),
            'test_data': {
                'random_value': i * 42,
                'test_string': f'test-data-{i}',
            }
        })
        
        # Small delay to spread out the logs
        time.sleep(0.01)
    
    total_time = time.time() - start_time
    total_log_entries = log_count * len(enabled_backends)
    
    app.logger.info("Stress test completed", extra={
        'stress_test_results': {
            'log_entries_generated': log_count,
            'backends_count': len(enabled_backends),
            'total_log_writes': total_log_entries,
            'duration_ms': round(total_time * 1000, 2),
            'logs_per_second': round(total_log_entries / total_time, 2),
        }
    })
    
    return jsonify({
        'message': f'Stress test completed: {log_count} log entries to {len(enabled_backends)} backend(s)',
        'results': {
            'log_entries': log_count,
            'backends': enabled_backends,
            'total_log_writes': total_log_entries,
            'duration_ms': round(total_time * 1000, 2),
            'performance': f'{round(total_log_entries / total_time, 2)} logs/second'
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with logging to all backends."""
    app.logger.warning("Page not found", extra={
        'error_type': '404_not_found',
        'requested_url': request.url,
        'method': request.method,
        'user_agent': request.headers.get('User-Agent'),
        'multi_backend_error_context': {
            'backends': enabled_backends,
            'error_correlation': True,
        }
    })
    
    return jsonify({
        'error': 'Page not found',
        'requested_url': request.url,
        'logged_to_backends': enabled_backends
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with logging to all backends."""
    app.logger.error("Internal server error", extra={
        'error_type': '500_internal_error',
        'error_message': str(error),
        'requested_url': request.url,
        'method': request.method,
        'multi_backend_error_tracking': {
            'backends': enabled_backends,
            'high_priority_alert': True,
        }
    }, exc_info=True)
    
    return jsonify({
        'error': 'Internal server error',
        'logged_to_backends': enabled_backends
    }), 500

if __name__ == '__main__':
    app.logger.info("Starting multi-backend Flask logging example", extra={
        'startup': True,
        'multi_backend_config': {
            'enabled_backends': enabled_backends,
            'backend_status': backend_status,
            'total_backends': len(enabled_backends),
            'environment': app.config.get('ENVIRONMENT')
        }
    })
    
    print(f"\n🚀 Multi-Backend Logging Flask App Started!")
    print(f"📊 Enabled backends: {', '.join(enabled_backends) if enabled_backends else 'None (check configuration)'}")
    print(f"🌐 Server: http://localhost:{os.getenv('PORT', 5000)}")
    print(f"📝 Logs are being sent to {len(enabled_backends)} backend(s) simultaneously")
    if not enabled_backends:
        print("⚠️  No backends enabled. Check your environment configuration!")
    print()
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config.get('ENVIRONMENT') == 'development'
    )
