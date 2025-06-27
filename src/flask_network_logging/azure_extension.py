"""
Azure Monitor Logs Extension for Flask Network Logging

This module provides the AzureLogExtension class for sending Flask application logs
to Azure Monitor Logs (Azure Log Analytics). It integrates with the flask-network-logging
package to provide comprehensive logging capabilities for Azure environments.
"""

import base64
import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

try:
    import requests
except ImportError:
    requests = None

from .context_filter import GraylogContextFilter
from .middleware import setup_middleware
from .middleware import setup_middleware


class AzureLogExtension:
    """
    Flask extension for sending logs to Azure Monitor Logs (Azure Log Analytics).

    This extension provides integration between Flask applications and Azure Monitor Logs,
    allowing for centralized logging in Azure environments. It supports automatic request
    context logging, custom fields, and configurable log levels.

    Features:
    - Automatic Azure Monitor Logs integration
    - Request context logging with user information
    - Configurable log levels and filtering
    - Custom field support
    - Environment-based configuration
    - Error handling and fallback logging

    Example:
        ```python
        from flask import Flask
        from flask_network_logging import AzureLogExtension

        app = Flask(__name__)
        app.config.update({
            'AZURE_WORKSPACE_ID': 'your-workspace-id',
            'AZURE_WORKSPACE_KEY': 'your-workspace-key',
            'AZURE_LOG_TYPE': 'FlaskAppLogs',
            'AZURE_LOG_LEVEL': 'INFO'
        })

        azure_log = AzureLogExtension(app)
        azure_log._setup_logging()

        # The extension uses a reusable context filter that works
        # with all flask-network-logging backends (Graylog, GCP, AWS, Azure)
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
        Initialize the Azure Monitor Logs extension.

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
        self.workspace_id = None
        self.workspace_key = None
        self.log_type = None
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

        # Initialize Azure Monitor configuration
        try:
            self._init_azure_config()
        except Exception as e:
            app.logger.warning(f"Failed to initialize Azure Monitor configuration: {e}")

        # Set up logging and middleware
        self._setup_logging()

    def _get_config_from_app(self) -> Dict[str, Any]:
        """
        Extract Azure Monitor configuration from Flask app config.

        Returns:
            Dictionary containing Azure Monitor configuration
        """
        if not self.app:
            return {}

        return {
            "AZURE_WORKSPACE_ID": self.app.config.get("AZURE_WORKSPACE_ID", os.getenv("AZURE_WORKSPACE_ID")),
            "AZURE_WORKSPACE_KEY": self.app.config.get("AZURE_WORKSPACE_KEY", os.getenv("AZURE_WORKSPACE_KEY")),
            "AZURE_LOG_TYPE": self.app.config.get("AZURE_LOG_TYPE", os.getenv("AZURE_LOG_TYPE", "FlaskAppLogs")),
            "AZURE_LOG_LEVEL": self.app.config.get("AZURE_LOG_LEVEL", os.getenv("AZURE_LOG_LEVEL", "INFO")),
            "AZURE_ENVIRONMENT": self.app.config.get(
                "AZURE_ENVIRONMENT", os.getenv("AZURE_ENVIRONMENT", "development")
            ),
            "AZURE_TIMEOUT": self.app.config.get("AZURE_TIMEOUT", os.getenv("AZURE_TIMEOUT", "30")),
        }

    def _init_azure_config(self):
        """Initialize Azure Monitor configuration."""
        if not requests:
            raise ImportError(
                "requests is required for Azure Monitor Logs support. "
                "Install it with: pip install flask-network-logging[azure]"
            )

        self.workspace_id = self.config.get("AZURE_WORKSPACE_ID")
        self.workspace_key = self.config.get("AZURE_WORKSPACE_KEY")
        self.log_type = self.config.get("AZURE_LOG_TYPE", "FlaskAppLogs")

        if not self.workspace_id or not self.workspace_key:
            if self.app:
                self.app.logger.warning("Azure Monitor Logs: Missing workspace ID or key")

    def _setup_logging(self):
        """
        Set up logging configuration for Azure Monitor Logs.

        This method configures the Flask application's logging to send logs to
        Azure Monitor Logs when in appropriate environments.
        """
        if not self.app:
            return

        # Prevent duplicate setup
        if self._logging_setup:
            return
        self._logging_setup = True

        # Re-read config in case it was updated after initialization
        self.config = self._get_config_from_app()

        # Check if we should set up Azure logging
        environment = self.config.get("AZURE_ENVIRONMENT", "development")

        # Only set up Azure logging in Azure environments or when explicitly configured
        if environment not in ["azure", "production"] and not self.config.get("AZURE_WORKSPACE_ID"):
            if environment == "development":
                self.app.logger.info("Azure Monitor Logs: Skipping setup in development environment")
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

        self.app.logger.info("Azure Monitor Logs extension initialized successfully")

    def _configure_logger(self, logger: logging.Logger, level: int):
        """
        Configure a specific logger with Azure Monitor handler.

        Args:
            logger: Logger instance to configure
            level: Log level to set
        """
        # Set log level
        logger.setLevel(level)

        # Create Azure Monitor handler if configuration is available
        if self.workspace_id and self.workspace_key and self.log_type:
            try:
                azure_handler = AzureMonitorHandler(
                    workspace_id=self.workspace_id,
                    workspace_key=self.workspace_key,
                    log_type=self.log_type,
                    timeout=int(self.config.get("AZURE_TIMEOUT", 30)),
                )
                azure_handler.setLevel(level)
                azure_handler.setFormatter(self.log_formatter)

                if self.context_filter:
                    azure_handler.addFilter(self.context_filter)

                logger.addHandler(azure_handler)

            except Exception as e:
                if self.app:
                    self.app.logger.warning(f"Failed to add Azure Monitor handler: {e}")

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


class AzureMonitorHandler(logging.Handler):
    """
    Custom logging handler for Azure Monitor Logs (Azure Log Analytics).

    This handler sends log records to Azure Monitor Logs using the HTTP Data Collector API.
    It handles authentication and error recovery for reliable log delivery.
    """

    def __init__(self, workspace_id: str, workspace_key: str, log_type: str, timeout: int = 30):
        """
        Initialize the Azure Monitor handler.

        Args:
            workspace_id: Azure Log Analytics workspace ID
            workspace_key: Azure Log Analytics workspace key
            log_type: Custom log type name
            timeout: HTTP request timeout in seconds
        """
        super().__init__()
        self.workspace_id = workspace_id
        self.workspace_key = workspace_key
        self.log_type = log_type
        self.timeout = timeout
        self.api_version = "2016-04-01"
        self.resource = "/api/logs"
        self.uri = f"https://{workspace_id}.ods.opinsights.azure.com{self.resource}?api-version={self.api_version}"

    def emit(self, record: logging.LogRecord):
        """
        Emit a log record to Azure Monitor Logs.

        Args:
            record: Log record to emit
        """
        try:
            # Format the log message
            message = self.format(record)

            # Prepare log data
            log_data = {
                "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
                "level": record.levelname,
                "logger": record.name,
                "message": message,
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
                "thread": record.thread,
                "process": record.process,
            }

            # Add any extra fields from the record
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
                    if not key.startswith("_"):
                        log_data[key] = str(value) if value is not None else None

            # Send to Azure Monitor
            self._send_log_data([log_data])

        except Exception:
            # Don't let logging errors break the application
            self.handleError(record)

    def _send_log_data(self, log_data: List[Dict[str, Any]]):
        """
        Send log data to Azure Monitor Logs.

        Args:
            log_data: List of log data dictionaries
        """
        if not requests:
            raise ImportError("requests library is required for Azure Monitor Logs")

        try:
            # Convert log data to JSON
            json_data = json.dumps(log_data)

            # Build the signature
            date_string = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
            content_length = len(json_data)

            string_to_hash = f"POST\n{content_length}\napplication/json\nx-ms-date:{date_string}\n{self.resource}"
            bytes_to_hash = bytes(string_to_hash, "UTF-8")
            decoded_key = base64.b64decode(self.workspace_key)
            encoded_hash = base64.b64encode(
                hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
            ).decode()
            authorization = f"SharedKey {self.workspace_id}:{encoded_hash}"

            # Build headers
            headers = {
                "content-type": "application/json",
                "Authorization": authorization,
                "Log-Type": self.log_type,
                "x-ms-date": date_string,
            }

            # Send POST request
            response = requests.post(self.uri, data=json_data, headers=headers, timeout=self.timeout)

            # Check response
            if response.status_code not in [200, 202]:
                raise Exception(f"Azure Monitor API returned status code {response.status_code}: {response.text}")

        except Exception:
            # Re-raise the exception to be handled by the emit method
            raise
