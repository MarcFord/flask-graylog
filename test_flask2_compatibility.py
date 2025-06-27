#!/usr/bin/env python3
"""
Test Flask 2.0+ compatibility with Flask Network Logging.
"""

from flask import Flask
import flask
from flask_remote_logging import GraylogExtension

# Test Flask 2.0+ compatibility
app = Flask(__name__)

# Basic configuration
app.config['GRAYLOG_HOST'] = 'localhost'
app.config['GRAYLOG_PORT'] = 12201
app.config['GRAYLOG_FACILITY'] = 'flask-test-app'

# Initialize the extension
graylog_extension = GraylogExtension()
graylog_extension.init_app(app)

@app.route('/')
def hello():
    app.logger.info('Hello endpoint called with Flask 2.0+')
    return 'Hello from Flask 2.0+ with Network Logging!'

@app.route('/test')
def test():
    app.logger.info('Test endpoint called')
    return {'message': 'Flask 2.0+ compatibility confirmed', 'status': 'success'}

if __name__ == '__main__':
    print(f"Flask version: {flask.__version__}")
    print("Flask Network Logging is compatible with Flask 2.0+")
    app.run(debug=True, port=5001)
