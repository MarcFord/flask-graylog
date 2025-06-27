#!/usr/bin/env python3
"""
Graylog Flask Example Application

This example demonstrates how to set up a Flask application that sends logs
to Graylog using GELF (Graylog Extended Log Format). This is the original
logging backend that this project was built for.

To run this example:
1. Set up your Graylog server
2. Configure the environment variables (see .env file)
3. Install dependencies: pip install flask-network-logging[graylog]
4. Run: python app.py
5. Visit http://localhost:5000

Environment Variables (see .env file):
- GRAYLOG_HOST: Your Graylog server hostname (default: localhost)
- GRAYLOG_PORT: Graylog GELF UDP port (default: 12201)
- GRAYLOG_LEVEL: Log level (default: INFO)
- GRAYLOG_ENVIRONMENT: Environment name (default: development)
"""

import os
import sys
from flask import Flask, request, jsonify, g
import time
import uuid

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from flask_remote_logging import GraylogExtension

app = Flask(__name__)

# Configure Graylog
app.config.update({
    'GRAYLOG_HOST': os.getenv('GRAYLOG_HOST', 'localhost'),
    'GRAYLOG_PORT': int(os.getenv('GRAYLOG_PORT', 12201)),
    'GRAYLOG_LEVEL': os.getenv('GRAYLOG_LEVEL', 'INFO'),
    'GRAYLOG_ENVIRONMENT': os.getenv('GRAYLOG_ENVIRONMENT', 'development'),
})

def get_current_user():
    """
    Example function to get current user information.
    In a real application, this would integrate with your authentication system.
    """
    return {
        'id': request.headers.get('X-User-ID', 'anonymous'),
        'username': request.headers.get('X-Username', 'guest'),
        'email': request.headers.get('X-User-Email', 'guest@example.com')
    }

# Initialize Graylog extension
graylog = GraylogExtension(app, get_current_user=get_current_user)

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
    })
    
    return response

@app.route('/')
def index():
    """Home page with API information."""
    app.logger.info("Home page accessed", extra={
        'endpoint': 'index',
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    })
    
    return jsonify({
        'message': 'Graylog Flask Example',
        'status': 'running',
        'logging_backend': 'Graylog (GELF)',
        'endpoints': {
            '/': 'This page',
            '/health': 'Health check',
            '/users': 'Mock users API',
            '/logs/test': 'Test different log levels',
            '/logs/user-context': 'Test user context logging',
            '/logs/error': 'Test error logging',
            '/logs/bulk': 'Test bulk logging'
        },
        'config': {
            'graylog_host': app.config.get('GRAYLOG_HOST'),
            'graylog_port': app.config.get('GRAYLOG_PORT'),
            'log_level': app.config.get('GRAYLOG_LEVEL'),
            'environment': app.config.get('GRAYLOG_ENVIRONMENT')
        }
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    app.logger.info("Health check requested", extra={
        'endpoint': 'health',
        'check_type': 'basic'
    })
    
    return jsonify({
        'status': 'healthy',
        'service': 'graylog-flask-example',
        'logging': 'enabled',
        'backend': 'graylog',
        'timestamp': time.time()
    })

@app.route('/users')
def users():
    """Mock users API endpoint."""
    app.logger.info("Users API endpoint accessed", extra={
        'endpoint': 'users',
        'action': 'list_users'
    })
    
    mock_users = [
        {'id': 1, 'username': 'alice', 'email': 'alice@example.com', 'active': True},
        {'id': 2, 'username': 'bob', 'email': 'bob@example.com', 'active': True},
        {'id': 3, 'username': 'charlie', 'email': 'charlie@example.com', 'active': False},
    ]
    
    return jsonify({
        'users': mock_users,
        'total': len(mock_users),
        'note': 'This request was logged to Graylog'
    })

@app.route('/logs/test')
def log_test():
    """Test different log levels."""
    request_id = g.request_id
    
    app.logger.debug("Debug message example", extra={
        'request_id': request_id,
        'log_type': 'debug_test',
        'test_data': {'level': 'debug', 'visible': False}
    })
    
    app.logger.info("Info message example", extra={
        'request_id': request_id,
        'log_type': 'info_test',
        'test_data': {'level': 'info', 'visible': True}
    })
    
    app.logger.warning("Warning message example", extra={
        'request_id': request_id,
        'log_type': 'warning_test',
        'test_data': {'level': 'warning', 'issue': 'minor'}
    })
    
    app.logger.error("Error message example", extra={
        'request_id': request_id,
        'log_type': 'error_test',
        'test_data': {'level': 'error', 'issue': 'major'}
    })
    
    return jsonify({
        'message': 'Log level test completed',
        'request_id': request_id,
        'levels_tested': ['debug', 'info', 'warning', 'error'],
        'note': 'Check your Graylog interface to see these logs with different severity levels'
    })

@app.route('/logs/user-context')
def user_context():
    """Test logging with user context."""
    user = get_current_user()
    
    app.logger.info("User context test", extra={
        'user_id': user['id'],
        'username': user['username'],
        'user_email': user['email'],
        'action': 'user_context_test',
        'session_info': {
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'request_id': g.request_id
        }
    })
    
    return jsonify({
        'message': 'User context logged successfully',
        'user': user,
        'request_id': g.request_id,
        'note': 'Check Graylog for rich user context information'
    })

@app.route('/logs/error')
def error_test():
    """Test error logging with exception handling."""
    try:
        # Intentionally cause an error for demonstration
        result = 1 / 0
        return jsonify({'result': result})
    except ZeroDivisionError as e:
        app.logger.error("Intentional division by zero error", extra={
            'error_type': 'ZeroDivisionError',
            'error_message': str(e),
            'endpoint': '/logs/error',
            'user_id': get_current_user()['id'],
            'request_id': g.request_id,
            'stack_trace': True
        }, exc_info=True)
        
        return jsonify({
            'error': 'Division by zero occurred',
            'message': 'This error has been logged to Graylog with full context',
            'request_id': g.request_id,
            'note': 'Check Graylog for the error log with stack trace'
        }), 500

@app.route('/logs/bulk')
def bulk_log_test():
    """Test bulk logging to demonstrate performance."""
    app.logger.info("Starting bulk log test", extra={
        'request_id': g.request_id,
        'test_type': 'bulk_logging'
    })
    
    # Generate multiple log entries
    for i in range(20):
        app.logger.info(f"Bulk log entry {i+1}", extra={
            'request_id': g.request_id,
            'bulk_test': True,
            'entry_number': i+1,
            'batch_size': 20,
            'test_data': {
                'random_field': f"value_{i}",
                'nested': {'level': i % 3, 'category': f"cat_{i % 5}"}
            }
        })
    
    app.logger.info("Bulk log test completed", extra={
        'request_id': g.request_id,
        'test_type': 'bulk_logging_complete',
        'total_entries': 20
    })
    
    return jsonify({
        'message': 'Bulk logging test completed',
        'entries_created': 22,  # 20 bulk + start + end
        'request_id': g.request_id,
        'note': 'Check Graylog to see all log entries with structured data'
    })

@app.route('/logs/structured')
def structured_logging():
    """Demonstrate structured logging with complex data."""
    complex_data = {
        'order_id': 'ORD-2025-001',
        'customer': {
            'id': 12345,
            'name': 'John Doe',
            'email': 'john@example.com',
            'tier': 'premium'
        },
        'items': [
            {'sku': 'ITEM-001', 'name': 'Widget A', 'price': 29.99, 'quantity': 2},
            {'sku': 'ITEM-002', 'name': 'Widget B', 'price': 49.99, 'quantity': 1}
        ],
        'payment': {
            'method': 'credit_card',
            'last_four': '1234',
            'amount': 109.97,
            'currency': 'USD'
        },
        'shipping': {
            'address': '123 Main St, Anytown, USA',
            'method': 'standard',
            'estimated_delivery': '2025-01-15'
        }
    }
    
    app.logger.info("Order processed successfully", extra={
        'request_id': g.request_id,
        'event_type': 'order_processed',
        'order_data': complex_data,
        'processing_time_ms': 150,
        'user_id': get_current_user()['id']
    })
    
    return jsonify({
        'message': 'Structured logging example completed',
        'order_data': complex_data,
        'request_id': g.request_id,
        'note': 'Check Graylog to see how complex structured data is handled'
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    app.logger.warning("Page not found", extra={
        'error_type': '404',
        'requested_url': request.url,
        'method': request.method,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent'),
        'request_id': getattr(g, 'request_id', 'unknown')
    })
    
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found',
        'request_id': getattr(g, 'request_id', 'unknown'),
        'note': 'This 404 error has been logged to Graylog'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    app.logger.error("Internal server error", extra={
        'error_type': '500',
        'error_message': str(error),
        'url': request.url,
        'method': request.method,
        'ip_address': request.remote_addr,
        'request_id': getattr(g, 'request_id', 'unknown')
    }, exc_info=True)
    
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'request_id': getattr(g, 'request_id', 'unknown'),
        'note': 'This error has been logged to Graylog with full context'
    }), 500

if __name__ == '__main__':
    print("🟡 Starting Graylog Flask Example...")
    print("📡 Logging backend: Graylog (GELF)")
    print(f"🏠 Graylog server: {app.config.get('GRAYLOG_HOST')}:{app.config.get('GRAYLOG_PORT')}")
    print("🌐 Server: http://localhost:5000")
    print("\n📋 Available endpoints:")
    print("   /                    - Home page with API info")
    print("   /health              - Health check")
    print("   /users               - Mock users API")
    print("   /logs/test           - Test different log levels")
    print("   /logs/user-context   - Test user context logging")
    print("   /logs/error          - Test error logging")
    print("   /logs/bulk           - Test bulk logging")
    print("   /logs/structured     - Test structured logging")
    print("\n🔍 Monitor logs in your Graylog web interface!")
    print("💡 Tip: Use headers X-User-ID, X-Username, X-User-Email to simulate different users")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
