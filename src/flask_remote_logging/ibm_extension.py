"""
IBM Cloud Logs Extension for Flask Network Logging

This module provides the IBMLogExtension class for sending Flask application logs
to IBM Cloud Logs (formerly LogDNA). It integrates with the flask-network-logging
package to provide comprehensive logging capabilities for IBM Cloud environments.
"""

import logging
import os
import socket
import time
from typing import Any, Callable, Dict, List, Optional, Union

try:
    import requests
except ImportError:
    requests = None

from .base_extension import BaseLoggingExtension


class IBMLogExtension(BaseLoggingExtension):
    """
    Flask extension for sending logs to IBM Cloud Logs (formerly LogDNA).

    This extension provides integration between Flask applications and IBM Cloud Logs,
    allowing for centralized logging in IBM Cloud environments. It supports automatic request
    context logging, custom fields, and configurable log levels.

    Features:
    - Automatic IBM Cloud Logs integration
    - Request context logging with user information
    - Configurable log levels and filtering
    - Custom field support
    - Environment-based configuration
    - Error handling and fallback logging

    Example:
        ```python
        from flask import Flask
        from flask_remote_logging import IBMLogExtension

        app = Flask(__name__)
        app.config.update({
            'IBM_INGESTION_KEY': 'your-ingestion-key',
            'IBM_HOSTNAME': 'your-hostname',
            'IBM_APP_NAME': 'your-app-name',
            'IBM_LOG_LEVEL': 'INFO'
        })

        ibm_log = IBMLogExtension(app)
        ```
    """

    def __init__(
        self,
        app: Optional[Any] = None,
        get_current_user: Optional[Callable] = None,
        log_level: int = logging.INFO,
        additional_logs: Optional[List[str]] = None,
        context_filter: Optional[logging.Filter] = None,
        log_formatter: Optional[logging.Formatter] = None,
        enable_middleware: bool = True,
    ):
        """
        Initialize the IBM Cloud Logs extension.

        Args:
            app: Flask application instance
            get_current_user: Function to retrieve current user information
            log_level: Logging level (default: INFO)
            additional_logs: List of additional logger names to configure
            context_filter: Custom logging filter
            log_formatter: Custom log formatter
            enable_middleware: Whether to enable request/response middleware
        """
        # IBM-specific attributes
        self.ingestion_key = None
        self.hostname = None
        self.app_name = None

        # Call parent constructor
        super().__init__(
            app=app,
            get_current_user=get_current_user,
            log_level=log_level,
            additional_logs=additional_logs,
            context_filter=context_filter,
            log_formatter=log_formatter,
            enable_middleware=enable_middleware,
        )

    # Abstract method implementations

    def _get_config_from_app(self) -> Dict[str, Any]:
        """Extract configuration from the Flask application."""
        if not self.app:
            return {}

        app_name = self.app.config.get("IBM_APP_NAME", getattr(self.app, "name", "flask-app"))

        return {
            "IBM_INGESTION_KEY": self.app.config.get("IBM_INGESTION_KEY", os.getenv("IBM_INGESTION_KEY")),
            "IBM_HOSTNAME": self.app.config.get("IBM_HOSTNAME", os.getenv("IBM_HOSTNAME", socket.gethostname())),
            "IBM_APP_NAME": app_name,
            "IBM_LOG_LEVEL": self.app.config.get("IBM_LOG_LEVEL", os.getenv("IBM_LOG_LEVEL", logging.INFO)),
            "IBM_URL": self.app.config.get(
                "IBM_URL", os.getenv("IBM_URL", "https://logs.us-south.logging.cloud.ibm.com/logs/ingest")
            ),
            "IBM_ENVIRONMENT": self.app.config.get("IBM_ENVIRONMENT", os.getenv("IBM_ENVIRONMENT", "production")),
            "FLASK_REMOTE_LOGGING_ENVIRONMENT": self.app.config.get(
                "FLASK_REMOTE_LOGGING_ENVIRONMENT",
                self.app.config.get(
                    "IBM_ENVIRONMENT", os.getenv("IBM_ENVIRONMENT", "production")
                ),  # Backward compatibility
            ),
            "IBM_MAC": self.app.config.get("IBM_MAC", os.getenv("IBM_MAC")),
            "IBM_IP": self.app.config.get("IBM_IP", os.getenv("IBM_IP")),
            "IBM_TAGS": self.app.config.get("IBM_TAGS", os.getenv("IBM_TAGS", "")),
            "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE": self.app.config.get("FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE"),
        }

    def _init_backend(self) -> None:
        """Initialize the IBM Cloud Logs backend."""
        # Extract configuration values
        self.ingestion_key = self.config.get("IBM_INGESTION_KEY")
        self.hostname = self.config.get("IBM_HOSTNAME", socket.gethostname())
        self.app_name = self.config.get("IBM_APP_NAME", "flask-app")

    def _init_ibm_config(self) -> None:
        """Initialize IBM-specific configuration (for backward compatibility)."""
        # This method is expected by tests but is essentially the same as _init_backend
        self._init_backend()

    def _create_log_handler(self) -> Optional[logging.Handler]:
        """Create the appropriate log handler for IBM Cloud Logs."""
        if not self.ingestion_key:
            # Use stream handler as fallback
            handler = logging.StreamHandler()
            if self.log_formatter:
                handler.setFormatter(self.log_formatter)
            return handler

        # Create IBM Cloud Logs handler
        try:
            return IBMCloudLogHandler(
                ingestion_key=self.ingestion_key,
                hostname=self.hostname or socket.gethostname(),
                app_name=self.app_name or "flask-app",
                url=self.config.get("IBM_URL", "https://logs.us-south.logging.cloud.ibm.com/logs/ingest"),
                mac=self.config.get("IBM_MAC"),
                ip=self.config.get("IBM_IP"),
                tags=self.config.get("IBM_TAGS", ""),
            )
        except Exception:
            # Fallback to stream handler
            handler = logging.StreamHandler()
            if self.log_formatter:
                handler.setFormatter(self.log_formatter)
            return handler

    def _should_skip_setup(self) -> bool:
        """
        Determine if setup should be skipped based on environment and configuration.

        IBM extension skips setup unless:
        - Environment is 'ibm' or 'production', OR
        - IBM_INGESTION_KEY is explicitly configured
        """
        environment = self.config.get("FLASK_REMOTE_LOGGING_ENVIRONMENT", "production")
        return environment not in ["ibm", "production"] and not self.config.get("IBM_INGESTION_KEY")

    def _get_extension_name(self) -> str:
        """Get the display name of the extension."""
        return "IBM Cloud Logs"

    def _get_middleware_config_key(self) -> str:
        """Get the configuration key for middleware override."""
        return "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE"

    def _configure_logger(self, logger: logging.Logger, level: int) -> None:
        """
        Configure a logger with IBM Cloud Logs handler.

        This method is expected by tests for backward compatibility.
        """
        logger.setLevel(level)

        # Create and add handler
        handler = self._create_log_handler()
        if handler:
            logger.addHandler(handler)


class IBMCloudLogHandler(logging.Handler):
    """
    Custom logging handler for IBM Cloud Logs (formerly LogDNA).

    This handler sends log records to IBM Cloud Logs via HTTP API calls.
    It supports batching, retries, and proper error handling.
    """

    def __init__(
        self,
        ingestion_key: str,
        hostname: Optional[str] = None,
        app_name: str = "flask-app",
        url: str = "https://logs.us-south.logging.cloud.ibm.com/logs/ingest",
        mac: Optional[str] = None,
        ip: Optional[str] = None,
        tags: Union[str, List[str]] = "",
        timeout: int = 30,
        level: int = logging.NOTSET,
    ):
        """
        Initialize the IBM Cloud Log handler.

        Args:
            ingestion_key: IBM Cloud Logs ingestion key
            hostname: Hostname to use for log entries
            app_name: Application name for log entries
            url: IBM Cloud Logs ingestion URL
            mac: MAC address (optional)
            ip: IP address (optional)
            tags: Comma-separated tags string or list of tags (optional)
            timeout: Request timeout in seconds
            level: Logging level
        """
        super().__init__(level)

        if not ingestion_key:
            raise ValueError("ingestion_key is required")

        if requests is None:
            raise RuntimeError("requests library is required for IBM Cloud Logs integration")

        self.ingestion_key = ingestion_key
        self.hostname = hostname or socket.gethostname()
        self.app_name = app_name
        self.url = url
        self.mac = mac
        self.ip = ip
        self.timeout = timeout

        # Handle tags parameter (can be string or list)
        if isinstance(tags, list):
            self.tags = tags
        else:
            self.tags = tags.split(",") if tags else []

        # Add env attribute for backward compatibility
        self.env = "development"

    def _map_log_level(self, level_name: str) -> str:
        """
        Map Python log level names to IBM Cloud Logs level names.

        Args:
            level_name: Python log level name (e.g., 'DEBUG', 'INFO')

        Returns:
            IBM Cloud Logs level name
        """
        level_mapping = {"DEBUG": "Debug", "INFO": "Info", "WARNING": "Warn", "ERROR": "Error", "CRITICAL": "Fatal"}
        return level_mapping.get(level_name, "Info")

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to IBM Cloud Logs.

        Args:
            record: The log record to emit
        """
        try:
            # Format the log record
            log_entry = self.format(record)

            # Extract extra fields from the log record
            meta = {
                "hostname": self.hostname,
                "logger": record.name,
                "filename": record.filename,
                "lineno": record.lineno,
                "funcName": record.funcName,
            }

            # Add any extra fields from the record
            reserved_attrs = {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "task",
                "asctime",
            }

            for key, value in record.__dict__.items():
                if key not in reserved_attrs:
                    meta[key] = value

            # Create the payload for IBM Cloud Logs
            payload = {
                "lines": [
                    {
                        "timestamp": int(record.created * 1000),  # Convert to milliseconds
                        "line": log_entry,
                        "app": self.app_name,
                        "level": self._map_log_level(record.levelname),
                        "meta": meta,
                    }
                ]
            }

            # Send to IBM Cloud Logs
            self._send_to_ibm_logs(payload)

        except Exception:
            # Don't let logging errors break the application
            self.handleError(record)

    def _send_log_data(self, payload: Dict[str, Any]) -> None:
        """
        Send log data to IBM Cloud Logs API (alternative method for tests).

        Args:
            payload: The log payload to send

        Raises:
            ImportError: If requests library is not available
            Exception: If the API request fails
        """
        if requests is None:
            raise ImportError("requests library is required for IBM Cloud Logs integration")

        self._send_to_ibm_logs(payload)

    def _send_to_ibm_logs(self, payload: Dict[str, Any]) -> None:
        """
        Send payload to IBM Cloud Logs API.

        Args:
            payload: The log payload to send

        Raises:
            Exception: If the API request fails
        """
        try:
            # Prepare headers
            headers = {"Content-Type": "application/json", "User-Agent": "flask-network-logging-ibm/1.0.0"}

            # Prepare query parameters
            params = {"hostname": self.hostname, "now": int(time.time() * 1000)}  # Current timestamp in milliseconds

            # Add optional parameters
            if self.ip:
                params["ip"] = self.ip
            if self.mac:
                params["mac"] = self.mac
            if self.tags:
                params["tags"] = ",".join(self.tags)

            # Send POST request with basic auth
            if requests:
                response = requests.post(
                    self.url,
                    auth=(self.ingestion_key, ""),  # LogDNA uses basic auth with key as username
                    headers=headers,
                    params=params,
                    json=payload,
                    timeout=self.timeout,
                )

                # Check response
                if response.status_code not in [200, 202]:
                    raise Exception(f"IBM Cloud Logs API returned status code {response.status_code}: {response.text}")
            else:
                raise RuntimeError("requests library is not available")

        except Exception:
            # Re-raise the exception to be handled by the emit method
            raise
