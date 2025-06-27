"""
Flask Network Logging Example Application

This example demonstrates how to use the flask-network-logging extension to send logs
to multiple remote logging services from a Flask application.

Features demonstrated:
- Graylog setup and configuration
- Google Cloud Logging setup and configuration  
- AWS CloudWatch Logs setup and configuration
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

from flask_remote_logging import GraylogExtension, GCPLogExtension, AWSLogExtension

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
    'AWS_LOG_GROUP': os.getenv('AWS_LOG_GROUP', '/aws/lambda/flask-network-logging-example'),
    'AWS_LOG_STREAM': os.getenv('AWS_LOG_STREAM', f'example-stream-{datetime.now().strftime("%Y-%m-%d")}'),
    'AWS_LOG_LEVEL': os.getenv('AWS_LOG_LEVEL', 'INFO'),
    'AWS_ENVIRONMENT': os.getenv('AWS_ENVIRONMENT', 'development'),
})

# Initialize all logging extensions
graylog = GraylogExtension(app)
gcp_log = GCPLogExtension(app)
aws_log = AWSLogExtension(app)

# Setup logging for all extensions

# Sample data for demonstration
USERS = [
    {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
    {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'},
    {'id': 3, 'name': 'Charlie', 'email': 'charlie@example.com'},
]

PRODUCTS = [
    {'id': 1, 'name': 'Laptop', 'price': 999.99, 'category': 'Electronics'},
    {'id': 2, 'name': 'Coffee Mug', 'price': 12.99, 'category': 'Home'},
    {'id': 3, 'name': 'Running Shoes', 'price': 89.99, 'category': 'Sports'},
]

def get_current_user():
    """
    Mock function to get current user information.
    In a real application, this would retrieve user data from session, JWT, etc.
    """
    # Simulate different users for demonstration
    user_ids = [1, 2, 3, None]
    user_id = random.choice(user_ids)
    
    if user_id:
        user = next((u for u in USERS if u['id'] == user_id), None)
        return user
    return None

@app.before_request
def before_request():
    """Set up request-specific data for logging."""
    # Generate a unique request ID for tracing
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()
    
    app.logger.info(
        f"Request started: {request.method} {request.path}",
        extra={
            'request_id': g.request_id,
            'request_method': request.method,
            'request_path': request.path,
            'user_agent': request.user_agent.string,
        }
    )

@app.after_request
def after_request(response):
    """Log request completion information."""
    duration = time.time() - g.start_time
    
    app.logger.info(
        f"Request completed: {request.method} {request.path} - {response.status_code}",
        extra={
            'request_id': g.request_id,
            'response_status': response.status_code,
            'response_time_ms': round(duration * 1000, 2),
            'request_method': request.method,
            'request_path': request.path,
        }
    )
    
    return response

@app.route('/')
def home():
    """Home endpoint with basic information."""
    app.logger.info("Home page accessed")
    
    return jsonify({
        'message': 'Flask Network Logging Example',
        'version': '1.0.0',
        'logging_backends': ['Graylog', 'Google Cloud Logging', 'AWS CloudWatch Logs'],
        'endpoints': [
            '/users',
            '/products', 
            '/test-logs',
            '/test-error',
            '/health'
        ]
    })

@app.route('/users')
def get_users():
    """Get all users - demonstrates INFO level logging."""
    app.logger.info(
        "Users endpoint accessed",
        extra={
            'endpoint': '/users',
            'total_users': len(USERS),
        }
    )
    
    return jsonify({
        'users': USERS,
        'total': len(USERS)
    })

@app.route('/users/<int:user_id>')
def get_user(user_id):
    """Get specific user - demonstrates conditional logging."""
    user = next((u for u in USERS if u['id'] == user_id), None)
    
    if user:
        app.logger.info(
            f"User {user_id} retrieved successfully",
            extra={
                'endpoint': '/users/<id>',
                'user_id': user_id,
                'user_name': user['name'],
            }
        )
        return jsonify(user)
    else:
        app.logger.warning(
            f"User {user_id} not found",
            extra={
                'endpoint': '/users/<id>',
                'user_id': user_id,
                'error_type': 'user_not_found',
            }
        )
        return jsonify({'error': 'User not found'}), 404

@app.route('/products')
def get_products():
    """Get all products with optional filtering."""
    category = request.args.get('category')
    
    if category:
        filtered_products = [p for p in PRODUCTS if p['category'].lower() == category.lower()]
        app.logger.info(
            f"Products filtered by category: {category}",
            extra={
                'endpoint': '/products',
                'filter_category': category,
                'filtered_count': len(filtered_products),
                'total_products': len(PRODUCTS),
            }
        )
        return jsonify({
            'products': filtered_products,
            'category': category,
            'total': len(filtered_products)
        })
    else:
        app.logger.info(
            "All products retrieved",
            extra={
                'endpoint': '/products',
                'total_products': len(PRODUCTS),
            }
        )
        return jsonify({
            'products': PRODUCTS,
            'total': len(PRODUCTS)
        })

@app.route('/test-logs')
def test_logs():
    """Test endpoint to demonstrate different log levels."""
    
    # DEBUG level
    app.logger.debug(
        "Debug message example",
        extra={
            'log_level_test': True,
            'test_type': 'debug',
            'timestamp': datetime.now().isoformat(),
        }
    )
    
    # INFO level
    app.logger.info(
        "Info message example",
        extra={
            'log_level_test': True,
            'test_type': 'info',
            'custom_data': {'key1': 'value1', 'key2': 42},
        }
    )
    
    # WARNING level
    app.logger.warning(
        "Warning message example",
        extra={
            'log_level_test': True,
            'test_type': 'warning',
            'warning_reason': 'demonstration_purpose',
        }
    )
    
    # ERROR level (without raising exception)
    app.logger.error(
        "Error message example",
        extra={
            'log_level_test': True,
            'test_type': 'error',
            'error_code': 'DEMO_ERROR',
            'severity': 'medium',
        }
    )
    
    return jsonify({
        'message': 'Log level test completed',
        'levels_tested': ['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        'note': 'Check your Graylog, Google Cloud Logging, and AWS CloudWatch for these messages'
    })

@app.route('/test-error')
def test_error():
    """Test endpoint to demonstrate error logging with exceptions."""
    
    error_type = request.args.get('type', 'generic')
    
    app.logger.info(
        f"Error test requested: {error_type}",
        extra={
            'endpoint': '/test-error',
            'error_type': error_type,
        }
    )
    
    try:
        if error_type == 'division':
            result = 10 / 0  # Division by zero
        elif error_type == 'key':
            data = {'a': 1}
            value = data['nonexistent_key']  # KeyError
        elif error_type == 'type':
            result = "string" + 42  # TypeError
        else:
            raise ValueError(f"Unknown error type: {error_type}")
            
    except Exception as e:
        app.logger.exception(
            f"Exception occurred in error test: {str(e)}",
            extra={
                'endpoint': '/test-error',
                'error_type': error_type,
                'exception_type': type(e).__name__,
                'exception_message': str(e),
            }
        )
        
        return jsonify({
            'error': 'Test exception occurred',
            'type': type(e).__name__,
            'message': str(e),
            'note': 'This is a test error for logging demonstration'
        }), 500
    
    return jsonify({'message': 'No error occurred'})

@app.route('/health')
def health_check():
    """Health check endpoint."""
    app.logger.debug("Health check performed")
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': 'N/A',  # In real app, calculate actual uptime
        'logging_status': {
            'graylog': 'configured',
            'gcp': 'configured' if app.config.get('GCP_PROJECT_ID') else 'not_configured',
            'aws': 'configured' if app.config.get('AWS_LOG_GROUP') else 'not_configured'
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    app.logger.warning(
        f"404 error: {request.path} not found",
        extra={
            'error_type': '404',
            'requested_path': request.path,
            'request_method': request.method,
        }
    )
    
    return jsonify({
        'error': 'Not found',
        'path': request.path,
        'method': request.method
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    app.logger.error(
        f"Internal server error: {str(error)}",
        extra={
            'error_type': '500',
            'error_message': str(error),
            'request_path': request.path,
            'request_method': request.method,
        }
    )
    
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    # Configure logging extensions with user context
    graylog.get_current_user = get_current_user
    gcp_log.get_current_user = get_current_user
    aws_log.get_current_user = get_current_user
    
    # Log application startup
    app.logger.info(
        "Flask Network Logging Example application starting",
        extra={
            'app_name': app.name,
            'debug_mode': app.debug,
            'graylog_host': app.config.get('GRAYLOG_HOST'),
            'gcp_project': app.config.get('GCP_PROJECT_ID', 'not_configured'),
            'aws_log_group': app.config.get('AWS_LOG_GROUP', 'not_configured'),
        }
    )
    
    # Start the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
