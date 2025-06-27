#!/usr/bin/env python3
"""
Test script to verify that all context filter aliases work correctly.
"""

from flask_network_logging import GraylogContextFilter, FlaskNetworkLoggingContextFilter, FNLContextFilter

def test_aliases():
    """Test that all aliases point to the same class."""
    
    # Create instances using different aliases
    graylog_filter = GraylogContextFilter()
    fnl_filter = FlaskNetworkLoggingContextFilter()
    short_filter = FNLContextFilter()
    
    # Check that they are all the same class
    assert type(graylog_filter) == type(fnl_filter) == type(short_filter)
    assert GraylogContextFilter == FlaskNetworkLoggingContextFilter == FNLContextFilter
    
    # Check that the class name is preserved for backward compatibility
    assert graylog_filter.__class__.__name__ == "GraylogContextFilter"
    assert fnl_filter.__class__.__name__ == "GraylogContextFilter"
    assert short_filter.__class__.__name__ == "GraylogContextFilter"
    
    print("✅ All context filter aliases work correctly!")
    print(f"   - GraylogContextFilter: {GraylogContextFilter}")
    print(f"   - FlaskNetworkLoggingContextFilter: {FlaskNetworkLoggingContextFilter}")
    print(f"   - FNLContextFilter: {FNLContextFilter}")
    
    # Test that name mangling still works for tests
    assert hasattr(graylog_filter, '_GraylogContextFilter__request')
    assert hasattr(fnl_filter, '_GraylogContextFilter__request')
    assert hasattr(short_filter, '_GraylogContextFilter__request')
    
    print("✅ Name mangling works correctly for all aliases!")

if __name__ == "__main__":
    test_aliases()
