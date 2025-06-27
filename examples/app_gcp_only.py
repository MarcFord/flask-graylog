"""
Flask Google Cloud Logging Example

This example demonstrates how to use the flask-network-logging extension 
specifically with Google Cloud Logging.

Features demonstrated:
- Google Cloud Logging setup and configuration
- Different log levels
- Request context logging
- Error handling with automatic logging
"""

import os
from flask import Flask, jsonify, request
from flask_remote_logging import GCPLogExtension

# Create Flask application
app = Flask(__name__)

# Configuration for Google Cloud Logging
app.config.update({
    'GCP_PROJECT_ID': os.getenv('GCP_PROJECT_ID', 'your-gcp-project-id'),
    'GCP_CREDENTIALS_PATH': os.getenv('GCP_CREDENTIALS_PATH'),  # Optional if using default credentials
    'GCP_LOG_NAME': os.getenv('GCP_LOG_NAME', 'flask-gcp-example'),
    'GCP_LOG_LEVEL': os.getenv('GCP_LOG_LEVEL', 'INFO'),
    'GCP_ENVIRONMENT': os.getenv('GCP_ENVIRONMENT', 'development'),
})

# Initialize GCP logging extension
gcp_log = GCPLogExtension(app)

# Setup logging

@app.route('/')
def home():
    """Home endpoint."""
    app.logger.info("Home page accessed via Google Cloud Logging")
    
    return jsonify({
        'message': 'Flask GCP Logging Example',
        'logging_backend': 'Google Cloud Logging',
        'project_id': app.config.get('GCP_PROJECT_ID', 'not_configured')
    })

@app.route('/test-log')
def test_log():
    """Test different log levels."""
    app.logger.debug("Debug log message")
    app.logger.info("Info log message", extra={'custom_field': 'test_value'})
    app.logger.warning("Warning log message")
    app.logger.error("Error log message")
    
    return jsonify({'message': 'Logs sent to Google Cloud Logging'})

@app.route('/test-error')
def test_error():
    """Test error logging."""
    try:
        # Intentional error for demonstration
        result = 10 / 0
    except Exception as e:
        app.logger.exception("Exception occurred in test endpoint")
        return jsonify({'error': str(e)}), 500
    
    return jsonify({'message': 'No error'})

if __name__ == '__main__':
    app.logger.info("Flask GCP Logging Example starting")
    app.run(host='0.0.0.0', port=5000, debug=True)
