#!/usr/bin/env python3
"""
Verification script to ensure the renamed package works correctly.
"""

print("🔍 Testing Flask Network Logging package...")

# Test basic imports
try:
    from flask_remote_logging import GraylogExtension, GCPLogExtension, Graylog, GCPLog
    print("✅ Main classes imported successfully")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test context filter import
try:
    from flask_remote_logging.context_filter import GraylogContextFilter
    print("✅ Context filter imported successfully")
except ImportError as e:
    print(f"❌ Context filter import failed: {e}")
    exit(1)

# Test version import
try:
    from flask_remote_logging import __version__
    print(f"✅ Version: {__version__}")
except ImportError as e:
    print(f"❌ Version import failed: {e}")
    exit(1)

# Test aliases
try:
    assert Graylog == GraylogExtension
    assert GCPLog == GCPLogExtension
    print("✅ Aliases working correctly")
except AssertionError:
    print("❌ Aliases not working correctly")
    exit(1)

# Test package docstring
try:
    import flask_remote_logging
    assert "Flask Remote Logging" in flask_remote_logging.__doc__
    print("✅ Package docstring updated correctly")
except AssertionError:
    print("❌ Package docstring not updated")
    exit(1)

print("\n🎉 All tests passed! The package has been successfully renamed to flask-network-logging")
print("\n📦 Directory structure:")
print("  src/flask_network_logging/")
print("    ├── __init__.py")
print("    ├── extension.py (Graylog)")
print("    ├── gcp_extension.py (Google Cloud)")
print("    └── context_filter.py")
print("\n🚀 Usage:")
print("  from flask_remote_logging import Graylog, GCPLog")
print("  from flask_remote_logging import GraylogExtension, GCPLogExtension")
