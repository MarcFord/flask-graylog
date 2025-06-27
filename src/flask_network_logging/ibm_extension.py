"""
IBM Cloud Logs Extension for Flask Network Logging

This module provides the IBMLogExtension class for sending Flask application logs
to IBM Cloud Logs (formerly LogDNA). It integrates with the flask-network-logging
package to provide comprehensive logging capabilities for IBM Cloud environments.
"""

import json
import logging
import os
import socket
import time
from typing import Any, Callable, Dict, List, Optional

try:
    import requests
except ImportError:
    requests = None

from .context_filter import GraylogContextFilter
from .middleware import setup_middleware


class IBMLogExtension:
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
        from flask_network_logging import IBMLogExtension

        app = Flask(__name__)
        app.config.update({
            'IBM_INGESTION_KEY': 'your-ingestion-key',
            'IBM_HOSTNAME': 'your-hostname',
            'IBM_APP_NAME': 'your-app-name',
            'IBM_LOG_LEVEL': 'INFO'
        })

        ibm_log = IBMLogExtension(app)
        ibm_log._setup_logging()

        # The extension uses a reusable context filter that works
        # with all flask-network-logging backends (Graylog, GCP, AWS, Azure, IBM)
        ```
    """

    def __init__(
        self,
        app=None,
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
            context_filter: Custom logging filter (if None, GraylogContextFilter is used)
            log_formatter: Custom log formatter
            enable_middleware: Whether to enable request/response middleware (default: True)
        """
        self.app = app
        self.get_current_user = get_current_user
        self.log_level = log_level
        self.additional_logs = additional_logs or []
        self.context_filter = context_filter
        self.log_formatter = log_formatter
        self.enable_middleware = enable_middleware
        self.config: dict[str, Any] = {}
        self.ingestion_key = None
        self.hostname = None
        self.app_name = None
        self._logging_setup: bool = False

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize the extension with a Flask application.

        Args:
            app: Flask application instance
        """
        self.app = app
        self.config = self._get_config_from_app()

        # Initialize IBM Cloud Logs configuration
        try:
            self._init_ibm_config()
        except Exception as e:
            app.logger.warning(f"Failed to initialize IBM Cloud Logs configuration: {e}")

        # Set up logging and middleware
        self._setup_logging()

    def _get_config_from_app(self) -> Dict[str, Any]:
        """
        Extract IBM Cloud Logs configuration from Flask app config.

        Returns:
            Dictionary containing IBM Cloud Logs configuration
        """
        if not self.app:
            return {}

        return {
            "IBM_INGESTION_KEY": self.app.config.get("IBM_INGESTION_KEY", os.getenv("IBM_INGESTION_KEY")),
            "IBM_HOSTNAME": self.app.config.get("IBM_HOSTNAME", os.getenv("IBM_HOSTNAME", socket.gethostname())),
            "IBM_IP": self.app.config.get("IBM_IP", os.getenv("IBM_IP")),
            "IBM_MAC": self.app.config.get("IBM_MAC", os.getenv("IBM_MAC")),
            "IBM_APP_NAME": self.app.config.get("IBM_APP_NAME", os.getenv("IBM_APP_NAME", "flask-app")),
            "IBM_ENV": self.app.config.get("IBM_ENV", os.getenv("IBM_ENV", "development")),
            "IBM_LOG_LEVEL": self.app.config.get("IBM_LOG_LEVEL", os.getenv("IBM_LOG_LEVEL", "INFO")),
            "IBM_ENVIRONMENT": self.app.config.get("IBM_ENVIRONMENT", os.getenv("IBM_ENVIRONMENT", "development")),
            "IBM_URL": self.app.config.get("IBM_URL", os.getenv("IBM_URL", "https://logs.logdna.com/logs/ingest")),
            "IBM_TIMEOUT": self.app.config.get("IBM_TIMEOUT", os.getenv("IBM_TIMEOUT", "30")),
            "IBM_INDEX_META": self.app.config.get(
                "IBM_INDEX_META", os.getenv("IBM_INDEX_META", "false").lower() == "true"
            ),
            "IBM_TAGS": self.app.config.get("IBM_TAGS", os.getenv("IBM_TAGS", "")),
        }

    def _init_ibm_config(self):
        """Initialize IBM Cloud Logs configuration."""
        if not requests:
            raise ImportError(
                "requests is required for IBM Cloud Logs support. "
                "Install it with: pip install flask-network-logging[ibm]"
            )

        self.ingestion_key = self.config.get("IBM_INGESTION_KEY")
        self.hostname = self.config.get("IBM_HOSTNAME", socket.gethostname())
        self.app_name = self.config.get("IBM_APP_NAME", "flask-app")

        if not self.ingestion_key:
            if self.app:
                self.app.logger.warning("IBM Cloud Logs: Missing ingestion key")

    def _setup_logging(self):
        """
        Set up logging configuration for IBM Cloud Logs.

        This method configures the Flask application's logging to send logs to
        IBM Cloud Logs when in appropriate environments.
        """
        if not self.app:
            return

        # Prevent duplicate setup
        if self._logging_setup:
            return
        self._logging_setup = True

        # Re-read config in case it was updated after initialization
        self.config = self._get_config_from_app()

        # Check if we should set up IBM logging
        environment = self.config.get("IBM_ENVIRONMENT", "development")

        # Only set up IBM logging in IBM environments or when explicitly configured
        if environment not in ["ibm", "production"] and not self.config.get("IBM_INGESTION_KEY"):
            if environment == "development":
                self.app.logger.info("IBM Cloud Logs: Skipping setup in development environment")
            return

        # Create context filter if not provided
        if not self.context_filter:
            self.context_filter = GraylogContextFilter(get_current_user=self.get_current_user)

        # Create log formatter if not provided
        if not self.log_formatter:
            self.log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Set up the main application logger
        self._configure_logger(self.app.logger, self.log_level)

        # Set up additional loggers
        for logger_name in self.additional_logs:
            logger = logging.getLogger(logger_name)
            self._configure_logger(logger, self.log_level)

        # Set up middleware if enabled
        if self.enable_middleware:
            setup_middleware(self.app)

        self.app.logger.info("IBM Cloud Logs extension initialized successfully")

    def _configure_logger(self, logger: logging.Logger, level: int):
        """
        Configure a specific logger with IBM Cloud Logs handler.

        Args:
            logger: Logger instance to configure
            level: Log level to set
        """
        # Set log level
        logger.setLevel(level)

        # Create IBM Cloud Logs handler if configuration is available
        if self.ingestion_key:
            try:
                # Parse tags if provided
                tags = []
                tags_str = self.config.get("IBM_TAGS", "")
                if tags_str:
                    tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]

                ibm_handler = IBMCloudLogHandler(
                    ingestion_key=self.ingestion_key,
                    hostname=self.hostname or socket.gethostname(),
                    app_name=self.app_name or "flask-app",
                    env=self.config.get("IBM_ENV", "development"),
                    ip=self.config.get("IBM_IP"),
                    mac=self.config.get("IBM_MAC"),
                    url=self.config.get("IBM_URL", "https://logs.logdna.com/logs/ingest"),
                    timeout=int(self.config.get("IBM_TIMEOUT", 30)),
                    index_meta=self.config.get("IBM_INDEX_META", False),
                    tags=tags,
                )
                ibm_handler.setLevel(level)
                ibm_handler.setFormatter(self.log_formatter)

                if self.context_filter:
                    ibm_handler.addFilter(self.context_filter)

                logger.addHandler(ibm_handler)

            except Exception as e:
                if self.app:
                    self.app.logger.warning(f"Failed to add IBM Cloud Logs handler: {e}")

        # Also add a stream handler for local development
        try:
            handlers = getattr(logger, "handlers", [])
            has_stream_handler = any(isinstance(h, logging.StreamHandler) for h in handlers)
        except (TypeError, AttributeError):
            has_stream_handler = False

        if not has_stream_handler:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(level)
            stream_handler.setFormatter(self.log_formatter)

            if self.context_filter:
                stream_handler.addFilter(self.context_filter)

            logger.addHandler(stream_handler)


class IBMCloudLogHandler(logging.Handler):
    """
    Custom logging handler for IBM Cloud Logs (formerly LogDNA).

    This handler sends log records to IBM Cloud Logs using the LogDNA ingestion API.
    It handles authentication and error recovery for reliable log delivery.
    """

    def __init__(
        self,
        ingestion_key: str,
        hostname: Optional[str] = None,
        app_name: str = "flask-app",
        env: str = "development",
        ip: Optional[str] = None,
        mac: Optional[str] = None,
        url: str = "https://logs.logdna.com/logs/ingest",
        timeout: int = 30,
        index_meta: bool = False,
        tags: Optional[List[str]] = None,
    ):
        """
        Initialize the IBM Cloud Logs handler.

        Args:
            ingestion_key: IBM Cloud Logs ingestion key
            hostname: Hostname for log entries
            app_name: Application name
            env: Environment name
            ip: IP address (optional)
            mac: MAC address (optional)
            url: LogDNA ingestion endpoint URL
            timeout: HTTP request timeout in seconds
            index_meta: Whether metadata should be indexed/searchable
            tags: List of tags for grouping hosts
        """
        super().__init__()
        self.ingestion_key = ingestion_key
        self.hostname = hostname or socket.gethostname()
        self.app_name = app_name
        self.env = env
        self.ip = ip
        self.mac = mac
        self.url = url
        self.timeout = timeout
        self.index_meta = index_meta
        self.tags = tags or []

    def emit(self, record: logging.LogRecord):
        """
        Emit a log record to IBM Cloud Logs.

        Args:
            record: Log record to emit
        """
        try:
            # Format the log message
            message = self.format(record)

            # Create log line data
            log_line = {
                "timestamp": int(record.created * 1000),  # Convert to milliseconds
                "line": message,
                "app": self.app_name,
                "level": self._map_log_level(record.levelname),
                "env": self.env,
            }

            # Add metadata if available
            meta = {}
            for key, value in record.__dict__.items():
                if key not in [
                    "name",
                    "msg",
                    "args",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
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
                    "stack_info",
                    "exc_info",
                    "exc_text",
                ]:
                    if not key.startswith("_") and value is not None:
                        try:
                            # Ensure the value is JSON serializable
                            json.dumps(value)
                            meta[key] = value
                        except (TypeError, ValueError):
                            meta[key] = str(value)

            # Add standard metadata
            meta.update(
                {
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                    "thread": record.thread,
                    "process": record.process,
                }
            )

            if meta:
                log_line["meta"] = meta
                if self.index_meta:
                    log_line["indexMeta"] = True

            # Prepare the payload
            payload = {"lines": [log_line]}

            # Send to IBM Cloud Logs
            self._send_log_data(payload)

        except Exception:
            # Don't let logging errors break the application
            self.handleError(record)

    def _map_log_level(self, python_level: str) -> str:
        """
        Map Python log levels to LogDNA log levels.

        Args:
            python_level: Python logging level name

        Returns:
            LogDNA log level name
        """
        level_mapping = {"DEBUG": "Debug", "INFO": "Info", "WARNING": "Warn", "ERROR": "Error", "CRITICAL": "Fatal"}
        return level_mapping.get(python_level, "Info")

    def _send_log_data(self, payload: Dict[str, Any]):
        """
        Send log data to IBM Cloud Logs.

        Args:
            payload: Log data payload
        """
        if not requests:
            raise ImportError("requests library is required for IBM Cloud Logs")

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

        except Exception:
            # Re-raise the exception to be handled by the emit method
            raise
