"""
Flask Network Logging - A Flask extension for integrating with remote logging services.

This package provides an easy-to-use interface for sending logs from a Flask application
to remote logging services including Graylog, Google Cloud Logging, and AWS CloudWatch Logs.
"""

# Dynamic version detection
try:
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version("flask_network_logging")
except ImportError:
    # Python < 3.8
    try:
        from importlib_metadata import PackageNotFoundError, version  # type: ignore

        __version__ = version("flask_network_logging")
    except ImportError:
        __version__ = "0.0.1-dev"
except (PackageNotFoundError, Exception):  # pylint: disable=broad-exception-caught
    # Fallback for development mode or package not installed
    __version__ = "0.0.1-dev"

from .context_filter import GraylogContextFilter, FlaskNetworkLoggingContextFilter, FNLContextFilter

# Import main classes for easy access
from .extension import GraylogExtension
from .gcp_extension import GCPLogExtension
from .aws_extension import AWSLogExtension
from .azure_extension import AzureLogExtension

# Create aliases for easier imports
Graylog = GraylogExtension
GCPLog = GCPLogExtension
AWSLog = AWSLogExtension
AzureLog = AzureLogExtension

__all__ = [
    "GraylogExtension", "GCPLogExtension", "AWSLogExtension", "AzureLogExtension",
    "Graylog", "GCPLog", "AWSLog", "AzureLog",
    "GraylogContextFilter", "FlaskNetworkLoggingContextFilter", "FNLContextFilter",  # Last two are aliases
    "__version__"
]
