"""
Flask Network Logging - A Flask extension for integrating with remote logging services.

This package provides an easy-to-use interface for sending logs from a Flask application
to remote logging services including Graylog and Google Cloud Logging.
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

from .context_filter import GraylogContextFilter

# Import main classes for easy access
from .extension import GraylogExtension
from .gcp_extension import GCPLogExtension

# Create aliases for easier imports
Graylog = GraylogExtension
GCPLog = GCPLogExtension

__all__ = ["GraylogExtension", "GCPLogExtension", "Graylog", "GCPLog", "GraylogContextFilter", "__version__"]
