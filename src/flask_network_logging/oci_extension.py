"""
Oracle Cloud Infrastructure (OCI) Logging Extension for Flask Network Logging

This module provides the OCILogExtension class for sending Flask application logs
to Oracle Cloud Infrastructure Logging. It integrates with the flask-network-logging package to
provide comprehensive logging capabilities for OCI environments.
"""

import json
import logging
import os
import socket
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

from .context_filter import GraylogContextFilter


class OCILogExtension:
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
        from flask_network_logging import OCILogExtension

        app = Flask(__name__)
        app.config.update({
            'OCI_CONFIG_PROFILE': 'DEFAULT',
            'OCI_LOG_GROUP_ID': 'ocid1.loggroup.oc1...',
            'OCI_LOG_ID': 'ocid1.log.oc1...',
            'OCI_LOG_LEVEL': 'INFO'
        })

        oci_log = OCILogExtension(app)
        oci_log._setup_logging()

        # The extension uses a reusable context filter that works
        # with all flask-network-logging backends (Graylog, GCP, AWS, Azure, IBM, OCI)
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
    ):
        """
        Initialize the OCI Logging extension.

        Args:
            app: Flask application instance
            get_current_user: Function to retrieve current user information
            log_level: Logging level (default: INFO)
            additional_logs: List of additional logger names to configure
            context_filter: Custom logging filter (if None, GraylogContextFilter is used)
            log_formatter: Custom log formatter
        """
        self.app = app
        self.get_current_user = get_current_user
        self.log_level = log_level
        self.additional_logs = additional_logs or []
        self.context_filter = context_filter
        self.log_formatter = log_formatter
        self.config = {}
        self.logging_client = None

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

        # Initialize OCI Logging client if OCI SDK is available
        try:
            self._init_oci_config()
        except Exception as e:
            app.logger.warning(f"Failed to initialize OCI Logging client: {e}")

    def _get_config_from_app(self) -> Dict[str, Any]:
        """
        Extract OCI Logging configuration from Flask app config.

        Returns:
            Dictionary containing OCI Logging configuration
        """
        if not self.app:
            return {}

        return {
            "OCI_CONFIG_FILE": self.app.config.get("OCI_CONFIG_FILE", os.getenv("OCI_CONFIG_FILE")),
            "OCI_CONFIG_PROFILE": self.app.config.get("OCI_CONFIG_PROFILE", os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")),
            "OCI_LOG_GROUP_ID": self.app.config.get("OCI_LOG_GROUP_ID", os.getenv("OCI_LOG_GROUP_ID")),
            "OCI_LOG_ID": self.app.config.get("OCI_LOG_ID", os.getenv("OCI_LOG_ID")),
            "OCI_COMPARTMENT_ID": self.app.config.get("OCI_COMPARTMENT_ID", os.getenv("OCI_COMPARTMENT_ID")),
            "OCI_SOURCE": self.app.config.get("OCI_SOURCE", os.getenv("OCI_SOURCE", "flask-app")),
            "OCI_LOG_LEVEL": self.app.config.get("OCI_LOG_LEVEL", os.getenv("OCI_LOG_LEVEL", "INFO")),
            "OCI_ENVIRONMENT": self.app.config.get("OCI_ENVIRONMENT", os.getenv("OCI_ENVIRONMENT", "development")),
        }

    def _init_oci_config(self):
        """Initialize the OCI Logging client."""
        if not oci:
            raise ImportError(
                "oci is required for Oracle Cloud Infrastructure Logging support. "
                "Install it with: pip install flask-network-logging[oci]"
            )

        try:
            # Create OCI config
            config_file = self.config.get("OCI_CONFIG_FILE")
            config_profile = self.config.get("OCI_CONFIG_PROFILE", "DEFAULT")

            if config_file:
                oci_config = oci.config.from_file(config_file, config_profile)
            else:
                # Try to load from default location
                oci_config = oci.config.from_file(profile_name=config_profile)

            # Validate the config
            oci.config.validate_config(oci_config)

            # Create the logging client
            self.logging_client = oci.logging.LoggingManagementClient(oci_config)

            if self.app:
                self.app.logger.info("OCI Logging client initialized successfully")

        except (ConfigFileNotFound, ServiceError, Exception) as e:
            if self.app:
                self.app.logger.warning(f"OCI Logging initialization failed: {e}")
            self.logging_client = None

    def _setup_logging(self):
        """
        Set up logging configuration for OCI Logging.

        This method configures the Flask application's logging to send logs to
        OCI Logging when in appropriate environments.
        """
        if not self.app:
            return

        # Re-read config in case it was updated after initialization
        self.config = self._get_config_from_app()

        # Check if we should set up OCI logging
        environment = self.config.get("OCI_ENVIRONMENT", "development")

        # Only set up OCI logging in Oracle Cloud environments or when explicitly configured
        if environment not in ["oci", "production"] and not self.config.get("OCI_LOG_ID"):
            if environment == "development":
                self.app.logger.info("OCI Logging: Skipping setup in development environment")
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

        self.app.logger.info("OCI Logging extension initialized successfully")

    def _configure_logger(self, logger: logging.Logger, level: int):
        """
        Configure a specific logger with OCI Logging handler.

        Args:
            logger: Logger instance to configure
            level: Log level to set
        """
        # Set log level
        logger.setLevel(level)

        # Create OCI handler if client is available and log ID is configured
        log_id = self.config.get("OCI_LOG_ID")
        if self.logging_client and log_id:
            try:
                oci_handler = OCILoggingHandler(
                    client=self.logging_client, log_id=log_id, source=self.config.get("OCI_SOURCE", "flask-app")
                )
                oci_handler.setLevel(level)
                oci_handler.setFormatter(self.log_formatter)

                if self.context_filter:
                    oci_handler.addFilter(self.context_filter)

                logger.addHandler(oci_handler)

            except Exception as e:
                if self.app:
                    self.app.logger.warning(f"Failed to add OCI Logging handler: {e}")

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


class OCILoggingHandler(logging.Handler):
    """
    Custom logging handler for Oracle Cloud Infrastructure Logging.

    This handler sends log records to OCI Logging using the OCI SDK client.
    It formats logs according to OCI Logging requirements and handles error recovery.
    """

    def __init__(self, client, log_id: str, source: str = "flask-app"):
        """
        Initialize the OCI Logging handler.

        Args:
            client: OCI logging management client
            log_id: OCI log OCID
            source: Source identifier for log entries
        """
        super().__init__()
        self.client = client
        self.log_id = log_id
        self.source = source
        self.hostname = socket.gethostname()

    def emit(self, record: logging.LogRecord):
        """
        Emit a log record to OCI Logging.

        Args:
            record: Log record to emit
        """
        try:
            # Format the log message
            message = self.format(record)

            # Create log entry
            log_entry = self._create_log_entry(record, message)

            # Send to OCI Logging
            self._send_log_entry(log_entry)

        except Exception as e:
            # Don't let logging errors break the application
            self.handleError(record)

    def _create_log_entry(self, record: logging.LogRecord, message: str) -> Dict[str, Any]:
        """
        Create an OCI log entry from a log record.

        Args:
            record: Log record
            message: Formatted log message

        Returns:
            Dictionary containing the log entry data
        """
        # Convert timestamp to ISO format
        timestamp = datetime.fromtimestamp(record.created).isoformat() + "Z"

        # Base log entry
        log_entry = {
            "timestamp": timestamp,
            "message": message,
            "source": self.source,
            "hostname": self.hostname,
            "level": record.levelname,
            "logger": record.name,
        }

        # Add extra fields from the record
        extra_fields = {}

        # Add request context fields if available
        for attr in [
            "request_id",
            "user_id",
            "username",
            "ip_address",
            "user_agent",
            "endpoint",
            "method",
            "url",
            "args",
            "form",
            "json",
        ]:
            if hasattr(record, attr):
                value = getattr(record, attr)
                if value is not None:
                    extra_fields[attr] = value

        # Add any other custom fields
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if (
                    key
                    not in [
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
                        "message",
                    ]
                    and not key.startswith("_")
                    and value is not None
                ):
                    extra_fields[key] = str(value)

        if extra_fields:
            log_entry["extra"] = json.dumps(extra_fields)

        return log_entry

    def _send_log_entry(self, log_entry: Dict[str, Any]):
        """
        Send a log entry to OCI Logging.

        Args:
            log_entry: Log entry dictionary
        """
        if not oci:
            raise ImportError("OCI SDK is required for OCI Logging support")

        try:
            # Create the log entry request
            put_logs_details = oci.logging.models.PutLogsDetails(
                specversion="1.0",
                log_entry_batches=[
                    oci.logging.models.LogEntryBatch(
                        entries=[
                            oci.logging.models.LogEntry(
                                data=json.dumps(log_entry),
                                id=f"{int(time.time())}-{hash(log_entry['message']) % 10000}",
                                time=log_entry["timestamp"],
                            )
                        ],
                        source=self.source,
                        type="application/json",
                    )
                ],
            )

            # Send the log entry
            self.client.put_logs(log_id=self.log_id, put_logs_details=put_logs_details)

        except ServiceError as e:
            # Re-raise service errors as they indicate configuration issues
            raise Exception(f"OCI Logging API error: {str(e)}")
        except Exception as e:
            # Re-raise other exceptions
            raise Exception(f"Failed to send log to OCI Logging: {str(e)}")

    def _map_log_level(self, level: str) -> str:
        """
        Map Python log level to OCI Logging level.

        Args:
            level: Python log level name

        Returns:
            OCI Logging compatible level
        """
        level_mapping = {"DEBUG": "DEBUG", "INFO": "INFO", "WARNING": "WARN", "ERROR": "ERROR", "CRITICAL": "FATAL"}
        return level_mapping.get(level.upper(), "INFO")
