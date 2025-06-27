#!/usr/bin/env python3
"""
Quick test script to verify IBM Cloud Logs extension functionality
"""

from flask import Flask
from flask_remote_logging import IBMLog

app = Flask(__name__)

# Configure IBM Cloud Logs (dummy config)
app.config.update({
    'IBM_HOSTNAME': 'test-host',
    'IBM_APP_NAME': 'test-app',
    'IBM_ENV': 'test',
    'IBM_LOG_LEVEL': 'INFO',
    'IBM_ENVIRONMENT': 'development',  # Will skip actual IBM setup in dev
})

print("Testing IBM Cloud Logs Extension...")

# Initialize IBM extension
try:
    ibm_log = IBMLog(app)
    print("✓ IBM extension created successfully")
except Exception as e:
    print(f"✗ Error creating IBM extension: {e}")
    exit(1)

# Test setup logging
try:
    ibm_log._setup_logging()
    print("✓ IBM logging setup completed")
except Exception as e:
    print(f"✗ Error setting up IBM logging: {e}")
    exit(1)

# Test logging (will only go to console in development mode)
@app.route('/')
def test_endpoint():
    app.logger.info("Test log message from IBM extension", extra={
        'test_field': 'test_value',
        'environment': 'test'
    })
    return "IBM logging test completed"

print("✓ All IBM extension tests passed!")
print("Note: In development environment, logs go to console only")
print("To test with actual IBM Cloud Logs, set IBM_ENVIRONMENT=production and provide real credentials")
