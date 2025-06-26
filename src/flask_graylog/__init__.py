"""
Flask Graylog - A Flask extension for integrating with Graylog.

This package provides an easy-to-use interface for sending logs from a Flask application
to a Graylog server.
"""

# Dynamic version detection
try:
    from importlib.metadata import PackageNotFoundError, version

    __version__ = version("flask_graylog")
except ImportError:
    # Python < 3.8
    try:
        from importlib_metadata import PackageNotFoundError, version  # type: ignore

        __version__ = version("flask_graylog")
    except ImportError:
        __version__ = "0.0.1-dev"
except (PackageNotFoundError, Exception):  # pylint: disable=broad-exception-caught
    # Fallback for development mode or package not installed
    __version__ = "0.0.1-dev"

from .context_filter import GraylogContextFilter

# Import main classes for easy access
from .extension import GraylogExtension

__all__ = ["GraylogExtension", "GraylogContextFilter", "__version__"]
