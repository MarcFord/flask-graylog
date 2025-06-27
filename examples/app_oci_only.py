#!/usr/bin/env python3
"""
Oracle Cloud Infrastructure (OCI) Logging Only Example

This example demonstrates how to set up a Flask application that sends logs only
to Oracle Cloud Infrastructure Logging. This is useful when you want to 
use OCI Logging as your primary logging backend in Oracle Cloud environments.

To use this example:
1. Set up your OCI Logging instance and get the log OCID
2. Configure your OCI CLI or create an OCI config file
3. Set the required environment variables (see below)
4. Run this script and visit http://localhost:5000

Required Environment Variables:
- OCI_LOG_ID: Your OCI log OCID (e.g., ocid1.log.oc1.us-ashburn-1....)

Optional Environment Variables:
- OCI_CONFIG_FILE: Path to OCI config file (default: ~/.oci/config)
- OCI_CONFIG_PROFILE: OCI config profile name (default: DEFAULT)
- OCI_LOG_GROUP_ID: OCI log group OCID
- OCI_COMPARTMENT_ID: OCI compartment OCID
- OCI_SOURCE: Source identifier for logs (default: flask-app)
- OCI_LOG_LEVEL: Logging level (default: INFO)
- OCI_ENVIRONMENT: Environment where logs should be sent (default: development)
"""

import os
from flask import Flask, request, jsonify
from flask_remote_logging import OCILogExtension

app = Flask(__name__)

# Configure OCI Logging
app.config.update({
    'OCI_CONFIG_FILE': os.getenv('OCI_CONFIG_FILE'),
    'OCI_CONFIG_PROFILE': os.getenv('OCI_CONFIG_PROFILE', 'DEFAULT'),
    'OCI_LOG_GROUP_ID': os.getenv('OCI_LOG_GROUP_ID'),
    'OCI_LOG_ID': os.getenv('OCI_LOG_ID'),
    'OCI_COMPARTMENT_ID': os.getenv('OCI_COMPARTMENT_ID'),
    'OCI_SOURCE': os.getenv('OCI_SOURCE', 'FlaskOCIExample'),
    'OCI_LOG_LEVEL': os.getenv('OCI_LOG_LEVEL', 'INFO'),
    'OCI_ENVIRONMENT': os.getenv('OCI_ENVIRONMENT', 'development'),
})

# Initialize OCI Logging extension (logging setup is automatic)
oci_log = OCILogExtension(app)

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

@app.route('/')
def index():
    """Home page with basic information."""
    app.logger.info("Home page accessed", extra={
        'endpoint': 'index',
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    })
    
    return jsonify({
        'message': 'Flask OCI Logging Example',
        'status': 'running',
        'endpoints': {
            '/': 'This page',
            '/info': 'Application information',
            '/log-test': 'Test different log levels',
            '/user-context': 'Test user context logging',
            '/error-test': 'Test error logging'
        }
    })

@app.route('/info')
def info():
    """Application information endpoint."""
    app.logger.info("Application info requested")
    
    return jsonify({
        'app_name': 'Flask OCI Logging Example',
        'logging_backend': 'Oracle Cloud Infrastructure Logging',
        'oci_config': {
            'config_profile': app.config.get('OCI_CONFIG_PROFILE'),
            'log_id': app.config.get('OCI_LOG_ID', 'Not configured'),
            'source': app.config.get('OCI_SOURCE'),
            'environment': app.config.get('OCI_ENVIRONMENT'),
            'log_level': app.config.get('OCI_LOG_LEVEL')
        }
    })

@app.route('/log-test')
def log_test():
    """Test different log levels."""
    app.logger.debug("This is a debug message")
    app.logger.info("This is an info message")
    app.logger.warning("This is a warning message")
    app.logger.error("This is an error message")
    
    return jsonify({
        'message': 'Log test completed',
        'levels_tested': ['debug', 'info', 'warning', 'error'],
        'note': 'Check your OCI Logging console to see the logs'
    })

@app.route('/user-context')
def user_context():
    """Test logging with user context."""
    user = get_current_user()
    
    app.logger.info("User context test", extra={
        'user_id': user['id'],
        'username': user['username'],
        'action': 'user_context_test',
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent')
    })
    
    return jsonify({
        'message': 'User context logged',
        'user': user,
        'note': 'Check OCI Logging for user context information'
    })

@app.route('/error-test')
def error_test():
    """Test error logging."""
    try:
        # Intentionally cause an error
        result = 1 / 0
        return jsonify({'result': result})
    except ZeroDivisionError as e:
        app.logger.error("Division by zero error occurred", extra={
            'error_type': 'ZeroDivisionError',
            'error_message': str(e),
            'endpoint': '/error-test',
            'user_id': get_current_user()['id']
        }, exc_info=True)
        
        return jsonify({
            'error': 'Division by zero',
            'message': 'This error has been logged to OCI Logging',
            'note': 'Check OCI Logging console for error details'
        }), 500

@app.route('/bulk-log-test')
def bulk_log_test():
    """Test bulk logging to stress test the OCI handler."""
    app.logger.info("Starting bulk log test")
    
    for i in range(10):
        app.logger.info(f"Bulk log message {i+1}", extra={
            'message_number': i+1,
            'test_type': 'bulk_logging',
            'timestamp': f"message_{i+1}"
        })
    
    app.logger.info("Bulk log test completed")
    
    return jsonify({
        'message': 'Bulk log test completed',
        'messages_sent': 12,  # 10 bulk + start + end messages
        'note': 'Check OCI Logging console for all messages'
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    app.logger.debug("Health check requested")
    
    return jsonify({
        'status': 'healthy',
        'logging': 'enabled',
        'backend': 'oci'
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    app.logger.warning("Page not found", extra={
        'requested_url': request.url,
        'method': request.method,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent')
    })
    
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found',
        'note': 'This 404 error has been logged to OCI Logging'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    app.logger.error("Internal server error", extra={
        'error': str(error),
        'url': request.url,
        'method': request.method,
        'ip_address': request.remote_addr
    }, exc_info=True)
    
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'note': 'This error has been logged to OCI Logging'
    }), 500

if __name__ == '__main__':
    # Check if required configuration is present
    if not app.config.get('OCI_LOG_ID'):
        print("Warning: OCI_LOG_ID not configured. Set the OCI_LOG_ID environment variable.")
        print("Example: export OCI_LOG_ID='ocid1.log.oc1.us-ashburn-1.example'")
    
    print("Starting Flask OCI Logging Example...")
    print("Visit http://localhost:5000 to test the application")
    print("Available endpoints:")
    print("  /               - Home page")
    print("  /info           - Application information")
    print("  /log-test       - Test different log levels")
    print("  /user-context   - Test user context logging")
    print("  /error-test     - Test error logging")
    print("  /bulk-log-test  - Test bulk logging")
    print("  /health         - Health check")
    print("\nCheck your OCI Logging console to see the logs in real-time!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
