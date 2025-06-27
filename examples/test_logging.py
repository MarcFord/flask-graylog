"""
Simple logging test script for the Flask Graylog example.

This script demonstrates how to use the flask-graylog extension
outside of the main Flask application for testing purposes.
"""

import sys
import time
from datetime import datetime

sys.path.insert(0, '../src')

from flask import Flask
from flask_remote_logging import GraylogExtension

# Create a minimal Flask app for testing
app = Flask(__name__)

# Configure Graylog
app.config.update({
    'GRAYLOG_HOST': 'localhost',
    'GRAYLOG_PORT': 12201,
    'GRAYLOG_LEVEL': 'DEBUG',
    'GRAYLOG_ENVIRONMENT': 'test',
    'GRAYLOG_FACILITY': 'test-script',
    'GRAYLOG_EXTRA_FIELDS': {
        'service': 'flask-graylog-test',
        'version': '1.0.0',
        'test_run': True,
    }
})

# Initialize Graylog extension
graylog = GraylogExtension(app)

def run_logging_tests():
    """Run a series of logging tests."""
    print("🧪 Starting Flask Graylog logging tests...")
    print("📡 Logs will be sent to Graylog at localhost:12201")
    print("")
    
    with app.app_context():
        test_id = int(time.time())
        
        # Test 1: Basic logging levels
        print("1️⃣ Testing basic logging levels...")
        app.logger.debug("Debug test message", extra={'test_id': test_id, 'test': 'debug'})
        app.logger.info("Info test message", extra={'test_id': test_id, 'test': 'info'})
        app.logger.warning("Warning test message", extra={'test_id': test_id, 'test': 'warning'})
        app.logger.error("Error test message", extra={'test_id': test_id, 'test': 'error'})
        app.logger.critical("Critical test message", extra={'test_id': test_id, 'test': 'critical'})
        time.sleep(1)
        
        # Test 2: Custom fields
        print("2️⃣ Testing custom fields...")
        app.logger.info("Custom fields test", extra={
            'test_id': test_id,
            'test': 'custom_fields',
            'user_id': 12345,
            'action': 'login',
            'ip_address': '192.168.1.100',
            'session_id': 'sess_abc123',
            'metadata': {
                'browser': 'Chrome',
                'os': 'Linux',
                'version': '1.2.3'
            }
        })
        time.sleep(1)
        
        # Test 3: Exception logging
        print("3️⃣ Testing exception logging...")
        try:
            raise ValueError("This is a test exception")
        except Exception:
            app.logger.error("Test exception occurred", extra={
                'test_id': test_id,
                'test': 'exception',
                'operation': 'test_exception_handling'
            }, exc_info=True)
        time.sleep(1)
        
        # Test 4: Performance logging
        print("4️⃣ Testing performance logging...")
        start_time = time.time()
        time.sleep(0.1)  # Simulate some work
        duration = time.time() - start_time
        
        app.logger.info("Performance test completed", extra={
            'test_id': test_id,
            'test': 'performance',
            'duration_ms': round(duration * 1000, 2),
            'operation': 'simulated_work',
            'status': 'success'
        })
        time.sleep(1)
        
        # Test 5: Bulk logging
        print("5️⃣ Testing bulk logging...")
        for i in range(5):
            app.logger.info(f"Bulk log message {i+1}", extra={
                'test_id': test_id,
                'test': 'bulk',
                'sequence': i + 1,
                'total': 5,
                'timestamp': datetime.utcnow().isoformat()
            })
            time.sleep(0.1)
        
        print("")
        print("✅ All tests completed!")
        print(f"🔍 Search for test_id:{test_id} in Graylog to see all test messages")
        print("")
        print("📊 Test Summary:")
        print("   • Basic logging levels: 5 messages")
        print("   • Custom fields: 1 message")
        print("   • Exception logging: 1 message") 
        print("   • Performance logging: 1 message")
        print("   • Bulk logging: 5 messages")
        print("   • Total: 13 messages")

if __name__ == '__main__':
    run_logging_tests()
