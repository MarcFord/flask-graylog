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

from flask import Flask

from .base_extension import BaseLoggingExtension


class AzureLogExtension(BaseLoggingExtension):
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
        from flask_remote_logging import AzureLogExtension

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
        app: Optional[Flask] = None,
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
            context_filter: Custom logging filter (if None, FlaskRemoteLoggingContextFilter is used)
            log_formatter: Custom log formatter
            enable_middleware: Whether to enable request/response middleware (default: True)
        """
        # Azure-specific attributes
        self.workspace_id = None
        self.workspace_key = None
        self.log_type = None

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

        # Azure extension expects additional_logs to be [] if None
        if self.additional_logs is None:
            self.additional_logs = []

    # Abstract method implementations

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
            "FLASK_REMOTE_LOGGING_ENVIRONMENT": self.app.config.get(
                "FLASK_REMOTE_LOGGING_ENVIRONMENT",
                self.app.config.get(
                    "AZURE_ENVIRONMENT", os.getenv("AZURE_ENVIRONMENT", "development")
                ),  # Backward compatibility
            ),
            "AZURE_TIMEOUT": self.app.config.get("AZURE_TIMEOUT", os.getenv("AZURE_TIMEOUT", "30")),
            "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE": self.app.config.get(
                "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE", None
            ),
        }

    def _init_backend(self) -> None:
        """Initialize the Azure Monitor backend."""
        try:
            self._init_azure_config()
        except Exception as e:
            if self.app:
                self.app.logger.warning(f"Failed to initialize Azure Monitor configuration: {e}")

    def _create_log_handler(self) -> Optional[logging.Handler]:
        """Create the appropriate log handler for Azure Monitor."""
        # Only set up Azure logging in Azure environments or when explicitly configured
        environment = self.config.get("AZURE_ENVIRONMENT", "development")

        if environment in ["azure", "production"] or self.config.get("AZURE_WORKSPACE_ID"):
            if self.workspace_id and self.workspace_key:
                # Create Azure Monitor handler
                handler = AzureMonitorHandler(
                    workspace_id=self.workspace_id,
                    workspace_key=self.workspace_key,
                    log_type=self.log_type or "FlaskAppLogs",
                )
                return handler
            else:
                # Fallback to stream handler if Azure not properly configured
                return logging.StreamHandler()
        else:
            # Return None to skip setup
            return None

    def _should_skip_setup(self) -> bool:
        """
        Determine if setup should be skipped based on environment and configuration.

        Azure extension skips setup unless:
        - Environment is 'azure' or 'production', OR
        - AZURE_WORKSPACE_ID is explicitly configured
        """
        environment = self.config.get("FLASK_REMOTE_LOGGING_ENVIRONMENT", "development")
        return environment not in ["azure", "production"] and not self.config.get("AZURE_WORKSPACE_ID")

    def _get_extension_name(self) -> str:
        """Get the display name of the extension."""
        return "Azure Monitor Logs"

    def _get_middleware_config_key(self) -> str:
        """Get the configuration key for middleware override."""
        return "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE"

    # Azure-specific helper methods

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
