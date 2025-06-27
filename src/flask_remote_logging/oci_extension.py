"""
Oracle Cloud Infrastructure (OCI) Logging Extension for Flask Network Logging

This module provides the OCILogExtension class for sending Flask application logs
to Oracle Cloud Infrastructure Logging. It integrates with the flask-network-logging package to
provide comprehensive logging capabilities for OCI environments.
"""

import logging
import os
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

try:
    import oci
    from oci.exceptions import ConfigFileNotFound, ServiceError
except ImportError:
    oci = None
    ServiceError = Exception
    ConfigFileNotFound = Exception

from .base_extension import BaseLoggingExtension


class OCILogExtension(BaseLoggingExtension):
    """
    Flask extension for sending logs to Oracle Cloud Infrastructure Logging.

    This extension provides integration between Flask applications and OCI Logging,
    allowing for centralized logging in Oracle Cloud environments. It supports automatic request
    context logging, custom fields, and configurable log levels.

    Features:
    - Automatic OCI Logging integration
    - Request context logging with user information
    - Configurable log levels and filtering
    - Custom field support
    - Environment-based configuration
    - Error handling and fallback logging

    Example:
        ```python
        from flask import Flask
        from flask_remote_logging import OCILogExtension

        app = Flask(__name__)
        app.config.update({
            'OCI_CONFIG_FILE': '~/.oci/config',
            'OCI_LOG_GROUP_ID': 'ocid1.loggroup.oc1...',
            'OCI_LOG_ID': 'ocid1.log.oc1...',
            'OCI_LOG_LEVEL': 'INFO'
        })

        oci_log = OCILogExtension(app)
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
        Initialize the OCI Logging extension.

        Args:
            app: Flask application instance
            get_current_user: Function to retrieve current user information
            log_level: Logging level (default: INFO)
            additional_logs: List of additional logger names to configure
            context_filter: Custom logging filter
            log_formatter: Custom log formatter
            enable_middleware: Whether to enable request/response middleware
        """
        # OCI-specific attributes
        self.logging_client = None
        self.log_group_id = None
        self.log_id = None

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

        app_name = self.app.config.get("OCI_APP_NAME", getattr(self.app, "name", "flask-app"))

        return {
            "OCI_CONFIG_FILE": self.app.config.get("OCI_CONFIG_FILE", os.getenv("OCI_CONFIG_FILE", "~/.oci/config")),
            "OCI_PROFILE": self.app.config.get("OCI_PROFILE", os.getenv("OCI_PROFILE", "DEFAULT")),
            "OCI_LOG_GROUP_ID": self.app.config.get("OCI_LOG_GROUP_ID", os.getenv("OCI_LOG_GROUP_ID")),
            "OCI_LOG_ID": self.app.config.get("OCI_LOG_ID", os.getenv("OCI_LOG_ID")),
            "OCI_APP_NAME": app_name,
            "OCI_LOG_LEVEL": self.app.config.get("OCI_LOG_LEVEL", os.getenv("OCI_LOG_LEVEL", logging.INFO)),
            "OCI_ENVIRONMENT": self.app.config.get("OCI_ENVIRONMENT", os.getenv("OCI_ENVIRONMENT", "production")),
            "FLASK_REMOTE_LOGGING_ENVIRONMENT": self.app.config.get(
                "FLASK_REMOTE_LOGGING_ENVIRONMENT",
                self.app.config.get(
                    "OCI_ENVIRONMENT", os.getenv("OCI_ENVIRONMENT", "production")
                ),  # Backward compatibility
            ),
            "OCI_REGION": self.app.config.get("OCI_REGION", os.getenv("OCI_REGION")),
            "OCI_COMPARTMENT_ID": self.app.config.get("OCI_COMPARTMENT_ID", os.getenv("OCI_COMPARTMENT_ID")),
            "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE": self.app.config.get("FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE"),
        }

    def _init_backend(self) -> None:
        """Initialize the OCI Logging backend."""
        if oci:
            try:
                # Initialize OCI config and logging client
                config_file = self.config.get("OCI_CONFIG_FILE", "~/.oci/config")
                profile = self.config.get("OCI_PROFILE", "DEFAULT")

                config = oci.config.from_file(config_file, profile)
                self.logging_client = oci.logging.LoggingManagementClient(config)

                # Store configuration values
                self.log_group_id = self.config.get("OCI_LOG_GROUP_ID")
                self.log_id = self.config.get("OCI_LOG_ID")

            except Exception:
                # If OCI initialization fails, we'll fallback to stream handler
                self.logging_client = None

    def _create_log_handler(self) -> Optional[logging.Handler]:
        """Create the appropriate log handler for OCI Logging."""
        if not self.logging_client or not self.log_group_id or not self.log_id:
            # Use stream handler as fallback
            handler = logging.StreamHandler()
            if self.log_formatter:
                handler.setFormatter(self.log_formatter)
            return handler

        # Create OCI Logging handler
        try:
            return OCILogHandler(
                logging_client=self.logging_client,
                log_group_id=self.log_group_id,
                log_id=self.log_id,
                app_name=self.config.get("OCI_APP_NAME", "flask-app"),
                region=self.config.get("OCI_REGION"),
                compartment_id=self.config.get("OCI_COMPARTMENT_ID"),
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

        OCI extension skips setup unless:
        - Environment is 'oci' or 'production', OR
        - OCI_LOG_GROUP_ID is explicitly configured
        """
        environment = self.config.get("FLASK_REMOTE_LOGGING_ENVIRONMENT", "production")
        return environment not in ["oci", "production"] and not self.config.get("OCI_LOG_GROUP_ID")

    def _get_extension_name(self) -> str:
        """Get the display name of the extension."""
        return "OCI Logging"

    def _get_middleware_config_key(self) -> str:
        """Get the configuration key for middleware override."""
        return "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE"


class OCILogHandler(logging.Handler):
    """
    Custom logging handler for Oracle Cloud Infrastructure Logging.

    This handler sends log records to OCI Logging via the OCI SDK.
    """

    def __init__(
        self,
        logging_client,
        log_group_id: str,
        log_id: str,
        app_name: str = "flask-app",
        region: Optional[str] = None,
        compartment_id: Optional[str] = None,
        level: int = logging.NOTSET,
    ):
        """
        Initialize the OCI Log handler.

        Args:
            logging_client: OCI Logging client
            log_group_id: OCI Log Group ID
            log_id: OCI Log ID
            app_name: Application name for log entries
            region: OCI region
            compartment_id: OCI compartment ID
            level: Logging level
        """
        super().__init__(level)

        if not logging_client:
            raise ValueError("logging_client is required")
        if not log_group_id:
            raise ValueError("log_group_id is required")
        if not log_id:
            raise ValueError("log_id is required")

        self.logging_client = logging_client
        self.log_group_id = log_group_id
        self.log_id = log_id
        self.app_name = app_name
        self.region = region
        self.compartment_id = compartment_id

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to OCI Logging.

        Args:
            record: The log record to emit
        """
        try:
            # Format the log record
            log_entry = self.format(record)

            # Create the log entry for OCI
            log_entry_data = {
                "time": datetime.fromtimestamp(record.created).isoformat() + "Z",
                "data": {
                    "message": log_entry,
                    "level": record.levelname,
                    "logger": record.name,
                    "filename": record.filename,
                    "lineno": record.lineno,
                    "funcName": record.funcName,
                    "app": self.app_name,
                },
            }

            # Send to OCI Logging
            self._send_to_oci_logging(log_entry_data)

        except Exception:
            # Don't let logging errors break the application
            self.handleError(record)

    def _send_to_oci_logging(self, log_entry: Dict[str, Any]) -> None:
        """
        Send log entry to OCI Logging.

        Args:
            log_entry: The log entry to send

        Raises:
            Exception: If the OCI API request fails
        """
        try:
            if oci:
                # Create the put logs request
                put_logs_details = oci.logging.models.PutLogsDetails(
                    specversion="1.0",
                    log_entry_batches=[
                        oci.logging.models.LogEntryBatch(
                            entries=[
                                oci.logging.models.LogEntry(
                                    data=log_entry["data"],
                                    id=str(int(time.time() * 1000)),  # Use timestamp as ID
                                    time=log_entry["time"],
                                )
                            ],
                            source=self.app_name,
                            type="application/json",
                        )
                    ],
                )

                # Send the logs
                self.logging_client.put_logs(
                    log_id=self.log_id,
                    put_logs_details=put_logs_details,
                )
            else:
                raise RuntimeError("OCI SDK is not available")

        except Exception:
            # Re-raise the exception to be handled by the emit method
            raise
