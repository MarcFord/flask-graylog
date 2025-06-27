import logging
import json
from typing import Any, Callable, Optional

from flask import Flask
from google.cloud import logging as cloud_logging
from google.cloud.logging_v2.handlers import CloudLoggingHandler

from .context_filter import GraylogContextFilter


class GCPLogExtension:
    """
    Flask extension for integrating with Google Cloud Logging.

    This extension provides an easy-to-use interface for sending logs from a Flask application
    to Google Cloud Logging.
    """

    def __init__(
        self,
        app: Optional[Flask] = None,
        get_current_user: Optional[Callable] = None,
        context_filter: Optional[logging.Filter] = None,
        log_formatter: Optional[logging.Formatter] = None,
        log_level: int = logging.INFO,
        additional_logs: Optional[list[str]] = None,
    ):
        self.context_filter: Optional[logging.Filter] = context_filter
        self.log_formatter: Optional[logging.Formatter] = log_formatter
        self.log_level: int = log_level
        self.additional_logs: Optional[list[str]] = additional_logs
        self.app: Optional[Flask] = None
        self.get_current_user: Optional[Callable] = get_current_user
        self.config: dict[str, Any] = {}
        self.cloud_logging_client: Optional[cloud_logging.Client] = None
        self._logging_setup: bool = False

        if app is not None:
            self.init_app(
                app,
                get_current_user=get_current_user,
                context_filter=context_filter,
                log_formatter=log_formatter,
                log_level=log_level,
                additional_logs=additional_logs,
            )

    def init_app(
        self,
        app: Flask,
        get_current_user: Optional[Callable] = None,
        context_filter: Optional[logging.Filter] = None,
        log_formatter: Optional[logging.Formatter] = None,
        log_level: int = logging.INFO,
        additional_logs: Optional[list[str]] = None,
    ) -> None:
        """
        Initialize the extension with the given Flask application.

        :param app: The Flask application instance.
        """
        self.app = app
        # Update instance attributes if provided
        if get_current_user:
            self.get_current_user = get_current_user
        if additional_logs:
            self.additional_logs = additional_logs
        if log_level != logging.INFO:  # Only update if explicitly changed from default
            self.log_level = log_level
        if log_formatter:
            self.log_formatter = log_formatter

        # Additional initialization logic can be added here.
        self.config = self._get_config_from_app()
        if not self.context_filter and not context_filter:
            self.context_filter = GraylogContextFilter(get_current_user=get_current_user or self.get_current_user)
        elif context_filter:
            self.context_filter = context_filter

        if not log_formatter and not self.log_formatter:
            self.log_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(hostname)s: %(message)s "
                "[in %(pathname)s:%(lineno)d]"
                "params: %(get_params)s"
            )
        elif log_formatter:
            self.log_formatter = log_formatter

        # Apply log_level parameter if provided, otherwise use config or default
        if log_level != logging.INFO:  # If explicitly set to non-default
            self.log_level = log_level
        else:
            self.log_level = self.config.get("GCP_LOG_LEVEL", self.log_level)

    def _setup_logging(self) -> None:
        """
        Configures logging for the Flask application based on the provided configuration.

        If the application's environment matches the configured GCP environment,
        sets up a Cloud Logging handler for logging to Google Cloud Logging. Otherwise, uses a standard
        stream handler with the specified log formatter.

        The log handler's level is set according to the configured log level. If a context
        filter is provided, it is added to the log handler and any additional loggers.

        The handler is attached to the Flask app's logger and to any additional loggers
        specified in the configuration.

        Raises:
            RuntimeError: If the extension is not initialized with a Flask app.
        """
        if not self.app:
            raise RuntimeError("GCPLogExtension must be initialized with a Flask app.")

        # Prevent duplicate setup
        if self._logging_setup:
            return
        
        self._logging_setup = True

        if str(self.app.env).lower() == self.config.get("GCP_ENVIRONMENT", "production").lower():
            try:
                # Initialize Cloud Logging client
                self.cloud_logging_client = cloud_logging.Client(
                    project=self.config.get("GCP_PROJECT_ID"),
                    credentials=None if not self.config.get("GCP_CREDENTIALS_PATH") else None
                )
                
                # Create Cloud Logging handler
                log_handler = CloudLoggingHandler(
                    self.cloud_logging_client,
                    name=self.config["GCP_LOG_NAME"],
                    labels={
                        "service_name": self.config["GCP_SERVICE_NAME"],
                        "app_name": self.config["GCP_APP_NAME"],
                        "environment": self.config["GCP_ENVIRONMENT"],
                    }
                )
            except Exception as e:
                # Fallback to stream handler if GCP setup fails
                print(f"Warning: Failed to setup Google Cloud Logging: {e}")
                log_handler = logging.StreamHandler()
                log_handler.setFormatter(self.log_formatter)
        else:
            log_handler = logging.StreamHandler()
            log_handler.setFormatter(self.log_formatter)

        log_handler.setLevel(self.log_level)

        if self.context_filter:
            log_handler.addFilter(self.context_filter)

        self.app.logger.addHandler(log_handler)
        # Set the logger level to ensure it passes messages to our handler
        self.app.logger.setLevel(self.log_level)

        if self.additional_logs:
            for log_name in self.additional_logs:
                additional_logger = logging.getLogger(log_name)
                additional_logger.setLevel(self.log_level)
                additional_logger.addHandler(log_handler)
                if self.context_filter:
                    additional_logger.addFilter(self.context_filter)

    def _get_config_from_app(self) -> dict[str, Any]:
        """
        Retrieve configuration settings from the Flask application.

        :return: A dictionary of configuration settings.
        """
        if not self.app:
            raise RuntimeError("GCPLogExtension must be initialized with a Flask app.")

        app_name = self.app.config.get("GCP_APP_NAME", self.app.name)

        return {
            "GCP_PROJECT_ID": self.app.config.get("GCP_PROJECT_ID"),
            "GCP_CREDENTIALS_PATH": self.app.config.get("GCP_CREDENTIALS_PATH"),
            "GCP_LOG_NAME": self.app.config.get("GCP_LOG_NAME", "flask-app"),
            "GCP_LOG_LEVEL": self.app.config.get("GCP_LOG_LEVEL", logging.INFO),
            "GCP_APP_NAME": app_name,
            "GCP_SERVICE_NAME": self.app.config.get("GCP_SERVICE_NAME", app_name),
            "GCP_ENVIRONMENT": self.app.config.get("GCP_ENVIRONMENT", "production"),
        }
