#!/usr/bin/env python3
"""
AWS CloudWatch Logs Flask Example Application

This example demonstrates how to set up a Flask application that sends logs
to AWS CloudWatch Logs. Perfect for applications running in AWS environments
like EC2, Lambda, ECS, or EKS.

To run this example:
1. Configure AWS credentials (AWS CLI, IAM roles, or environment variables)
2. Set up CloudWatch Log Groups and Streams
3. Configure environment variables (see .env file)
4. Install dependencies: pip install flask-network-logging[aws]
5. Run: python app.py
6. Visit http://localhost:5000

Environment Variables (see .env file):
- AWS_REGION: AWS region (default: us-east-1)
- AWS_ACCESS_KEY_ID: AWS access key (optional if using IAM roles)
- AWS_SECRET_ACCESS_KEY: AWS secret key (optional if using IAM roles)
- AWS_LOG_GROUP: CloudWatch log group name
- AWS_LOG_STREAM: CloudWatch log stream name
- AWS_LOG_LEVEL: Log level (default: INFO)
- AWS_ENVIRONMENT: Environment name (default: development)
"""

import os
import sys
from flask import Flask, request, jsonify, g
import time
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from flask_remote_logging import AWSLogExtension

app = Flask(__name__)

# Configure AWS CloudWatch Logs
app.config.update({
    'AWS_REGION': os.getenv('AWS_REGION', 'us-east-1'),
    'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
    'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
    'AWS_LOG_GROUP': os.getenv('AWS_LOG_GROUP', '/aws/flask-app/logs'),
    'AWS_LOG_STREAM': os.getenv('AWS_LOG_STREAM', 'application-logs'),
    'AWS_LOG_LEVEL': os.getenv('AWS_LOG_LEVEL', 'INFO'),
    'AWS_ENVIRONMENT': os.getenv('AWS_ENVIRONMENT', 'development'),
    'AWS_CREATE_LOG_GROUP': os.getenv('AWS_CREATE_LOG_GROUP', 'true').lower() == 'true',
    'AWS_CREATE_LOG_STREAM': os.getenv('AWS_CREATE_LOG_STREAM', 'true').lower() == 'true',
})

def get_current_user():
    """
    Example function to get current user information.
    In AWS environments, this might integrate with Cognito, IAM, or other auth services.
    """
    return {
        'id': request.headers.get('X-User-ID', 'anonymous'),
        'username': request.headers.get('X-Username', 'guest'),
        'email': request.headers.get('X-User-Email', 'guest@example.com'),
        'aws_user_arn': request.headers.get('X-AWS-User-ARN', 'arn:aws:iam::123456789012:user/guest')
    }

# Initialize AWS CloudWatch Logs extension
aws_log = AWSLogExtension(app, get_current_user=get_current_user)

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
        'aws_request_id': request.headers.get('X-Amz-Request-Id', 'local'),
        'aws_trace_id': request.headers.get('X-Amzn-Trace-Id', 'local'),
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
        'aws_region': app.config.get('AWS_REGION'),
    })
    
    return response

@app.route('/')
def index():
    """Home page with API information."""
    app.logger.info("Home page accessed", extra={
        'endpoint': 'index',
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'cloudwatch_info': {
            'log_group': app.config.get('AWS_LOG_GROUP'),
            'log_stream': app.config.get('AWS_LOG_STREAM'),
            'region': app.config.get('AWS_REGION')
        }
    })
    
    return jsonify({
        'message': 'AWS CloudWatch Logs Flask Example',
        'status': 'running',
        'logging_backend': 'AWS CloudWatch Logs',
        'endpoints': {
            '/': 'This page',
            '/health': 'Health check',
            '/users': 'Mock users API',
            '/logs/test': 'Test different log levels',
            '/logs/user-context': 'Test user context logging',
            '/logs/error': 'Test error logging',
            '/logs/aws-metrics': 'Test AWS-specific metrics',
            '/logs/performance': 'Test performance logging'
        },
        'aws_config': {
            'region': app.config.get('AWS_REGION'),
            'log_group': app.config.get('AWS_LOG_GROUP'),
            'log_stream': app.config.get('AWS_LOG_STREAM'),
            'environment': app.config.get('AWS_ENVIRONMENT')
        }
    })

@app.route('/health')
def health():
    """Health check endpoint with AWS metadata."""
    app.logger.info("Health check requested", extra={
        'endpoint': 'health',
        'check_type': 'aws_health',
        'aws_metadata': {
            'region': app.config.get('AWS_REGION'),
            'service': 'flask-app',
            'log_group': app.config.get('AWS_LOG_GROUP')
        }
    })
    
    return jsonify({
        'status': 'healthy',
        'service': 'aws-cloudwatch-flask-example',
        'logging': 'enabled',
        'backend': 'aws-cloudwatch',
        'aws_region': app.config.get('AWS_REGION'),
        'log_group': app.config.get('AWS_LOG_GROUP'),
        'timestamp': time.time()
    })

@app.route('/users')
def users():
    """Mock users API endpoint with AWS context."""
    app.logger.info("Users API endpoint accessed", extra={
        'endpoint': 'users',
        'action': 'list_users',
        'aws_service': 'cloudwatch-logs',
        'data_classification': 'internal'
    })
    
    mock_users = [
        {'id': 1, 'username': 'alice-aws', 'email': 'alice@aws-example.com', 'role': 'admin'},
        {'id': 2, 'username': 'bob-dev', 'email': 'bob@aws-example.com', 'role': 'developer'},
        {'id': 3, 'username': 'charlie-ops', 'email': 'charlie@aws-example.com', 'role': 'ops'},
    ]
    
    return jsonify({
        'users': mock_users,
        'total': len(mock_users),
        'aws_region': app.config.get('AWS_REGION'),
        'note': 'This request was logged to AWS CloudWatch Logs'
    })

@app.route('/logs/test')
def log_test():
    """Test different log levels in CloudWatch context."""
    request_id = g.request_id
    
    app.logger.debug("CloudWatch debug message", extra={
        'request_id': request_id,
        'log_type': 'debug_test',
        'aws_context': {'service': 'flask', 'environment': 'test'},
        'test_data': {'level': 'debug', 'visible_in_cloudwatch': False}
    })
    
    app.logger.info("CloudWatch info message", extra={
        'request_id': request_id,
        'log_type': 'info_test',
        'aws_context': {'service': 'flask', 'environment': 'test'},
        'test_data': {'level': 'info', 'visible_in_cloudwatch': True}
    })
    
    app.logger.warning("CloudWatch warning message", extra={
        'request_id': request_id,
        'log_type': 'warning_test',
        'aws_context': {'service': 'flask', 'environment': 'test'},
        'test_data': {'level': 'warning', 'requires_attention': True}
    })
    
    app.logger.error("CloudWatch error message", extra={
        'request_id': request_id,
        'log_type': 'error_test',
        'aws_context': {'service': 'flask', 'environment': 'test'},
        'test_data': {'level': 'error', 'creates_alarm': True}
    })
    
    return jsonify({
        'message': 'CloudWatch log level test completed',
        'request_id': request_id,
        'levels_tested': ['debug', 'info', 'warning', 'error'],
        'aws_log_group': app.config.get('AWS_LOG_GROUP'),
        'note': 'Check AWS CloudWatch Logs console to see these logs'
    })

@app.route('/logs/user-context')
def user_context():
    """Test logging with user context in AWS environment."""
    user = get_current_user()
    
    app.logger.info("AWS user context test", extra={
        'user_id': user['id'],
        'username': user['username'],
        'user_email': user['email'],
        'aws_user_arn': user['aws_user_arn'],
        'action': 'user_context_test',
        'aws_session': {
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'request_id': g.request_id,
            'region': app.config.get('AWS_REGION'),
            'log_group': app.config.get('AWS_LOG_GROUP')
        }
    })
    
    return jsonify({
        'message': 'AWS user context logged successfully',
        'user': user,
        'request_id': g.request_id,
        'aws_region': app.config.get('AWS_REGION'),
        'note': 'Check CloudWatch Logs for rich AWS user context'
    })

@app.route('/logs/error')
def error_test():
    """Test error logging with AWS-specific context."""
    try:
        # Intentionally cause an error for demonstration
        result = 1 / 0
        return jsonify({'result': result})
    except ZeroDivisionError as e:
        app.logger.error("AWS CloudWatch error example", extra={
            'error_type': 'ZeroDivisionError',
            'error_message': str(e),
            'endpoint': '/logs/error',
            'user_id': get_current_user()['id'],
            'request_id': g.request_id,
            'aws_context': {
                'region': app.config.get('AWS_REGION'),
                'log_group': app.config.get('AWS_LOG_GROUP'),
                'log_stream': app.config.get('AWS_LOG_STREAM'),
                'service': 'flask-app'
            },
            'stack_trace': True
        }, exc_info=True)
        
        return jsonify({
            'error': 'Division by zero occurred',
            'message': 'This error has been logged to AWS CloudWatch Logs',
            'request_id': g.request_id,
            'aws_log_group': app.config.get('AWS_LOG_GROUP'),
            'note': 'Check CloudWatch Logs for the error with full AWS context'
        }), 500

@app.route('/logs/aws-metrics')
def aws_metrics():
    """Log AWS-specific metrics and performance data."""
    metrics_data = {
        'memory_usage': {
            'used_mb': 256,
            'available_mb': 768,
            'percentage': 25.0
        },
        'cpu_usage': {
            'percentage': 15.5,
            'load_average': [0.2, 0.3, 0.1]
        },
        'disk_usage': {
            'used_gb': 8.5,
            'available_gb': 15.5,
            'percentage': 35.4
        },
        'network': {
            'bytes_in': 1024000,
            'bytes_out': 512000,
            'connections': 5
        }
    }
    
    app.logger.info("AWS system metrics", extra={
        'request_id': g.request_id,
        'metric_type': 'system_performance',
        'aws_metrics': metrics_data,
        'aws_context': {
            'region': app.config.get('AWS_REGION'),
            'instance_type': 't3.micro',  # Example
            'availability_zone': f"{app.config.get('AWS_REGION')}a"
        },
        'timestamp': time.time()
    })
    
    return jsonify({
        'message': 'AWS metrics logged successfully',
        'metrics': metrics_data,
        'request_id': g.request_id,
        'note': 'Check CloudWatch Logs for system performance metrics'
    })

@app.route('/logs/performance')
def performance_test():
    """Test performance logging with AWS context."""
    start_time = time.time()
    
    # Simulate some work
    import time as time_module
    time_module.sleep(0.1)  # 100ms delay
    
    processing_time = time.time() - start_time
    
    app.logger.info("Performance test completed", extra={
        'request_id': g.request_id,
        'performance_metrics': {
            'processing_time_ms': round(processing_time * 1000, 2),
            'operation': 'simulated_work',
            'success': True
        },
        'aws_performance': {
            'region': app.config.get('AWS_REGION'),
            'log_group': app.config.get('AWS_LOG_GROUP'),
            'cloudwatch_latency_estimate': '< 1s'
        }
    })
    
    return jsonify({
        'message': 'Performance test completed',
        'processing_time_ms': round(processing_time * 1000, 2),
        'request_id': g.request_id,
        'note': 'Check CloudWatch Logs for performance metrics'
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with AWS context."""
    app.logger.warning("Page not found in AWS environment", extra={
        'error_type': '404',
        'requested_url': request.url,
        'method': request.method,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'request_id': getattr(g, 'request_id', 'unknown'),
        'aws_context': {
            'region': app.config.get('AWS_REGION'),
            'log_group': app.config.get('AWS_LOG_GROUP')
        }
    })
    
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found',
        'request_id': getattr(g, 'request_id', 'unknown'),
        'aws_region': app.config.get('AWS_REGION'),
        'note': 'This 404 error has been logged to AWS CloudWatch Logs'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with AWS context."""
    app.logger.error("Internal server error in AWS environment", extra={
        'error_type': '500',
        'error_message': str(error),
        'url': request.url,
        'method': request.method,
        'ip_address': request.remote_addr,
        'request_id': getattr(g, 'request_id', 'unknown'),
        'aws_context': {
            'region': app.config.get('AWS_REGION'),
            'log_group': app.config.get('AWS_LOG_GROUP'),
            'log_stream': app.config.get('AWS_LOG_STREAM')
        }
    }, exc_info=True)
    
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'request_id': getattr(g, 'request_id', 'unknown'),
        'aws_region': app.config.get('AWS_REGION'),
        'note': 'This error has been logged to AWS CloudWatch Logs with full context'
    }), 500

if __name__ == '__main__':
    print("🟠 Starting AWS CloudWatch Logs Flask Example...")
    print("☁️ Logging backend: AWS CloudWatch Logs")
    print(f"🌍 AWS region: {app.config.get('AWS_REGION')}")
    print(f"📋 Log group: {app.config.get('AWS_LOG_GROUP')}")
    print(f"📄 Log stream: {app.config.get('AWS_LOG_STREAM')}")
    print("🌐 Server: http://localhost:5000")
    print("\n📋 Available endpoints:")
    print("   /                      - Home page with API info")
    print("   /health                - Health check with AWS metadata")
    print("   /users                 - Mock users API")
    print("   /logs/test             - Test different log levels")
    print("   /logs/user-context     - Test user context logging")
    print("   /logs/error            - Test error logging")
    print("   /logs/aws-metrics      - Test AWS-specific metrics")
    print("   /logs/performance      - Test performance logging")
    print("\n🔍 Monitor logs in AWS CloudWatch Logs console!")
    print("💡 Tip: Use headers X-User-ID, X-Username, X-User-Email, X-AWS-User-ARN to simulate different users")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
