"""
Flask Graylog Example Application

This example demonstrates how to use the flask-graylog extension to send logs
to a Graylog server from a Flask application.

Features demonstrated:
- Basic Graylog setup and configuration
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

from flask_remote_logging import GraylogExtension
from flask_remote_logging.compat import set_flask_env

# Create Flask application
app = Flask(__name__)

# Configuration for Graylog
app.config.update({
    # Graylog server configuration
    'GRAYLOG_HOST': os.getenv('GRAYLOG_HOST', 'localhost'),
    'GRAYLOG_PORT': int(os.getenv('GRAYLOG_PORT', 12201)),
    # Log level configuration
    'GRAYLOG_LEVEL': os.getenv('GRAYLOG_LEVEL', 'INFO'),
    # Environment configuration (logs will only be sent if app.env matches this)
    # Note: FLASK_REMOTE_LOGGING_ENVIRONMENT is the new unified key (v2.0+)
    # Old key GRAYLOG_ENVIRONMENT still works for backward compatibility
    'FLASK_REMOTE_LOGGING_ENVIRONMENT': os.getenv('FLASK_REMOTE_LOGGING_ENVIRONMENT', 'development'),
})

# Initialize Graylog extension
graylog = GraylogExtension(app)

# Sample data for demonstration
USERS = [
    {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
    {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'},
    {'id': 3, 'name': 'Charlie', 'email': 'charlie@example.com'},
]

PRODUCTS = [
    {'id': 1, 'name': 'Laptop', 'price': 999.99, 'stock': 10},
    {'id': 2, 'name': 'Mouse', 'price': 29.99, 'stock': 50},
    {'id': 3, 'name': 'Keyboard', 'price': 79.99, 'stock': 25},
]

@app.route('/')
def index():
    """Home page with basic information."""
    app.logger.info("Home page accessed", extra={
        'endpoint': 'index',
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    })
    
    return jsonify({
        'message': 'Welcome to Flask Graylog Example!',
        'endpoints': {
            '/': 'This page',
            '/users': 'List all users',
            '/users/<id>': 'Get specific user',
            '/products': 'List all products',
            '/products/<id>': 'Get specific product',
            '/log-test': 'Test different log levels',
            '/simulate-error': 'Simulate an error for testing',
            '/simulate-warning': 'Simulate a warning',
            '/health': 'Health check endpoint'
        },
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/users')
def list_users():
    """List all users."""
    app.logger.info("Users list requested", extra={
        'endpoint': 'list_users',
        'total_users': len(USERS)
    })
    
    return jsonify({
        'users': USERS,
        'total': len(USERS),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/users/<int:user_id>')
def get_user(user_id):
    """Get a specific user by ID."""
    user = next((u for u in USERS if u['id'] == user_id), None)
    
    if user:
        app.logger.info("User retrieved successfully")
        return jsonify(user)
    else:
        app.logger.warning("User not found")
        return jsonify({'error': 'User not found'}), 404

@app.route('/products')
def list_products():
    """List all products."""
    app.logger.info("Products list requested")
    
    return jsonify({
        'products': PRODUCTS,
        'total': len(PRODUCTS),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/products/<int:product_id>')
def get_product(product_id):
    """Get a specific product by ID."""
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    
    if product:
        app.logger.info("Product retrieved successfully")
        return jsonify(product)
    else:
        app.logger.warning("Product not found")
        return jsonify({'error': 'Product not found'}), 404

@app.route('/log-test')
def log_test():
    """Test different log levels."""
    test_id = random.randint(1000, 9999)
    
    # Test different log levels
    app.logger.debug("Debug message for testing")
    
    app.logger.info("Info message for testing")
    
    app.logger.warning("Warning message for testing")
    
    app.logger.error("Error message for testing")
    
    app.logger.critical("Critical message for testing")
    
    return jsonify({
        'message': 'Log test completed',
        'test_id': test_id,
        'levels_tested': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        'note': 'Check your Graylog server for the log messages'
    })

@app.route('/simulate-error')
def simulate_error():
    """Simulate an error for testing error handling."""
    error_types = ['division_by_zero', 'key_error', 'type_error', 'value_error']
    error_type = random.choice(error_types)
    
    app.logger.info(f"Simulating error for testing: {error_type}")
    
    try:
        if error_type == 'division_by_zero':
            result = 10 / 0
        elif error_type == 'key_error':
            data = {'key': 'value'}
            result = data['nonexistent_key']
        elif error_type == 'type_error':
            result = 'string' + 5
        elif error_type == 'value_error':
            result = int('not_a_number')
        
        return jsonify({'result': result})
        
    except Exception as e:
        app.logger.error(e)
        
        return jsonify({
            'error': 'Simulated error occurred',
            'type': error_type,
            'message': str(e)
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    app.logger.debug("Health check performed")
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'graylog_configured': True,
        'environment': app.config.get('GRAYLOG_ENVIRONMENT', 'unknown')
    })

@app.before_request
def before_request():
    """Log request information before processing."""
    request_uuid = request.headers.get("Request-ID", None)
    if not request_uuid:
        request_uuid = uuid.uuid4().hex

    g.request_uuid = request_uuid

    app.logger.debug("Request received")

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    app.logger.warning("404 Not Found")
    
    return jsonify({
        'error': 'Not Found',
        'message': f"The requested URL {request.path} was not found",
        'status_code': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    app.logger.error(error)
    
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'status_code': 500
    }), 500

if __name__ == '__main__':
    # Set Flask environment (compatible with Flask 1.x and 2.x)
    flask_env = os.getenv('FLASK_ENV', 'development')
    set_flask_env(app, flask_env)
    
    # Log application startup
    app.logger.info("Flask application starting")
    
    # Run the application
    try:
        app.run(
            host=os.getenv('FLASK_HOST', '127.0.0.1'),
            port=int(os.getenv('FLASK_PORT', 5000)),
            debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
        )
    except KeyboardInterrupt:
        app.logger.info("Application shutdown requested")
    except Exception as e:
        app.logger.critical("Application failed to start", extra={
            'error': str(e),
            'exception_type': type(e).__name__
        }, exc_info=True)
        raise
