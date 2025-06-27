#!/usr/bin/env python3
"""
Azure Monitor Logs Only Example

This example demonstrates how to set up a Flask application that sends logs only
to Azure Monitor Logs (Azure Log Analytics). This is useful when you want to 
use Azure Monitor as your primary logging backend in Azure environments.

To use this example:
1. Set up your Azure Log Analytics workspace
2. Set the required environment variables (see below)
3. Run this script and visit http://localhost:5000

Required Environment Variables:
- AZURE_WORKSPACE_ID: Your Azure Log Analytics workspace ID
- AZURE_WORKSPACE_KEY: Your Azure Log Analytics workspace key

Optional Environment Variables:
- AZURE_LOG_TYPE: Custom log type name (default: FlaskAppLogs)
- AZURE_LOG_LEVEL: Logging level (default: INFO)
- AZURE_ENVIRONMENT: Environment name (default: production)
"""

import os
from flask import Flask, request, jsonify
from flask_remote_logging import AzureLogExtension

app = Flask(__name__)

# Configure Azure Monitor Logs
app.config.update({
    'AZURE_WORKSPACE_ID': os.getenv('AZURE_WORKSPACE_ID'),
    'AZURE_WORKSPACE_KEY': os.getenv('AZURE_WORKSPACE_KEY'),
    'AZURE_LOG_TYPE': os.getenv('AZURE_LOG_TYPE', 'FlaskAppLogs'),
    'AZURE_LOG_LEVEL': os.getenv('AZURE_LOG_LEVEL', 'INFO'),
    'AZURE_ENVIRONMENT': os.getenv('AZURE_ENVIRONMENT', 'production'),
    'AZURE_TIMEOUT': os.getenv('AZURE_TIMEOUT', '30'),
})

# Initialize Azure Monitor extension (logging setup is automatic)
azure_log = AzureLogExtension(app)

@app.route('/')
def index():
    """Main page - demonstrates basic info logging."""
    app.logger.info("Index page accessed", extra={
        'endpoint': '/',
        'method': request.method,
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    })
    
    return jsonify({
        'message': 'Azure Monitor Logs Example App',
        'status': 'success',
        'logging_backend': 'Azure Monitor Logs',
        'workspace_id': app.config.get('AZURE_WORKSPACE_ID', 'Not configured'),
        'log_type': app.config.get('AZURE_LOG_TYPE'),
        'endpoints': [
            '/ - This page',
            '/health - Health check',
            '/api/users - Sample API endpoint',
            '/error - Trigger an error for testing',
            '/debug - Debug level logging example'
        ]
    })

@app.route('/health')
def health_check():
    """Health check endpoint."""
    app.logger.info("Health check requested")
    return jsonify({'status': 'healthy', 'service': 'flask-azure-logging-example'})

@app.route('/api/users')
def api_users():
    """Sample API endpoint with structured logging."""
    app.logger.info("Users API endpoint accessed", extra={
        'api_endpoint': '/api/users',
        'operation': 'list_users',
        'user_count': 3
    })
    
    users = [
        {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
        {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'},
        {'id': 3, 'name': 'Charlie', 'email': 'charlie@example.com'}
    ]
    
    return jsonify({'users': users, 'count': len(users)})

@app.route('/error')
def trigger_error():
    """Endpoint that triggers an error for testing error logging."""
    app.logger.warning("About to trigger an intentional error for testing")
    
    try:
        # Intentionally trigger an error
        result = 1 / 0
    except ZeroDivisionError as e:
        app.logger.error("Intentional error triggered for testing", extra={
            'error_type': 'ZeroDivisionError',
            'error_message': str(e),
            'endpoint': '/error'
        })
        return jsonify({
            'error': 'Intentional error for testing',
            'message': 'Check your Azure Monitor Logs for error details'
        }), 500

@app.route('/debug')
def debug_example():
    """Endpoint demonstrating debug level logging."""
    app.logger.debug("Debug information", extra={
        'debug_data': {
            'step': 1,
            'process': 'example_debug',
            'details': 'This is debug level information'
        }
    })
    
    app.logger.info("Debug endpoint accessed successfully")
    
    return jsonify({
        'message': 'Debug logging example',
        'note': 'Debug logs may not appear unless AZURE_LOG_LEVEL is set to DEBUG'
    })

if __name__ == '__main__':
    # Check if required configuration is present
    workspace_id = app.config.get('AZURE_WORKSPACE_ID')
    workspace_key = app.config.get('AZURE_WORKSPACE_KEY')
    
    if not workspace_id or not workspace_key:
        print("Warning: Azure Monitor Logs not fully configured.")
        print("Set AZURE_WORKSPACE_ID and AZURE_WORKSPACE_KEY environment variables.")
        print("Logs will only be sent to console until Azure Monitor is configured.")
    else:
        print(f"Azure Monitor Logs configured for workspace: {workspace_id}")
        print(f"Log type: {app.config.get('AZURE_LOG_TYPE')}")
    
    print("Starting Flask app on http://localhost:5000")
    print("Available endpoints:")
    print("  / - Main page")
    print("  /health - Health check")
    print("  /api/users - Sample API")
    print("  /error - Trigger error")
    print("  /debug - Debug logging")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
