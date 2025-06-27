"""
GCP Cloud Logging extension for Flask applications.

This module provides a Flask extension for sending logs to Google Cloud Logging.
"""

import logging
from typing import Any, Callable, Dict, Optional

from flask import Flask

try:
    from google.cloud import logging as cloud_logging
    from google.cloud.logging_v2.handlers import CloudLoggingHandler
except ImportError:
    cloud_logging = None
    CloudLoggingHandler = None

from .base_extension import BaseLoggingExtension


class GCPLogExtension(BaseLoggingExtension):
    """
    Flask extension for integrating with Google Cloud Logging.

    This extension provides an easy-to-use interface for sending logs from a Flask application
    to Google Cloud Logging.
    """

    def __init__(
        self,
        app: Optional[Flask] = None,
        get_current_user: Optional[Callable] = None,
        log_level: int = logging.INFO,
        additional_logs: Optional[list[str]] = None,
        context_filter: Optional[logging.Filter] = None,
        log_formatter: Optional[logging.Formatter] = None,
        enable_middleware: bool = True,
    ):
        """
        Initialize the GCP logging extension.

        Args:
            app: Flask application instance
            get_current_user: Function to retrieve current user information
            log_level: Logging level (default: INFO)
            additional_logs: List of additional logger names to configure
            context_filter: Custom logging filter
            log_formatter: Custom log formatter
            enable_middleware: Whether to enable request/response middleware
        """
        # GCP-specific attributes
        self.cloud_logging_client = None
        self._original_log_level = log_level  # Store the original parameter

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

    def _get_config_from_app(self) -> Dict[str, Any]:
        """
        Extract configuration from the Flask application.

        Returns:
            Dictionary containing the extension's configuration
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
            "FLASK_REMOTE_LOGGING_ENVIRONMENT": self.app.config.get(
                "FLASK_REMOTE_LOGGING_ENVIRONMENT",
                self.app.config.get("GCP_ENVIRONMENT", "production"),  # Backward compatibility
            ),
            "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE": self.app.config.get("FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE"),
        }

    def _init_backend(self) -> None:
        """
        Initialize the GCP Cloud Logging backend.
        """
        if cloud_logging and self.config.get("GCP_PROJECT_ID"):
            try:
                self.cloud_logging_client = cloud_logging.Client(
                    project=self.config.get("GCP_PROJECT_ID"),
                    credentials=None if not self.config.get("GCP_CREDENTIALS_PATH") else None,
                )
            except Exception as e:
                if self.app:
                    print(f"Warning: Failed to setup Google Cloud Logging: {e}")  # Print warning for test compatibility

    def _create_log_handler(self) -> Optional[logging.Handler]:
        """
        Create the appropriate log handler for GCP Cloud Logging.

        Returns:
            A logging.Handler instance configured for GCP Cloud Logging,
            or None if setup should be skipped
        """
        # Check if we should use GCP Cloud Logging
        if (
            self.cloud_logging_client
            and CloudLoggingHandler
            and self.app
            and str(self._get_flask_env()).lower() == self.config.get("GCP_ENVIRONMENT", "production").lower()
        ):

            try:
                # Create GCP Cloud Logging handler
                return CloudLoggingHandler(
                    self.cloud_logging_client,
                    name=self.config.get("GCP_LOG_NAME", "flask-app"),
                    labels={
                        "service_name": self.config.get("GCP_SERVICE_NAME", getattr(self.app, "name", "flask-app")),
                        "app_name": self.config.get("GCP_APP_NAME", getattr(self.app, "name", "flask-app")),
                        "environment": self.config.get("GCP_ENVIRONMENT", "production"),
                    },
                )
            except Exception as e:
                # Fallback to stream handler if GCP setup fails
                if self.app:
                    print(f"Warning: Failed to setup Google Cloud Logging: {e}")  # Print warning for test compatibility

        # Use stream handler as fallback
        handler = logging.StreamHandler()
        if self.log_formatter:
            handler.setFormatter(self.log_formatter)
        return handler

    def _should_skip_setup(self) -> bool:
        """
        Determine if logging setup should be skipped based on environment or config.

        GCP extension skips setup only if:
        - GCP_PROJECT_ID is not configured AND
        - Current Flask environment doesn't match target environment

        Returns:
            True if setup should be skipped, False otherwise
        """
        # Only skip if GCP is explicitly not configured and environment doesn't match
        environment = self.config.get("FLASK_REMOTE_LOGGING_ENVIRONMENT", "production")
        if not self.config.get("GCP_PROJECT_ID") and self.app:
            app_env = self._get_flask_env()
            return bool(str(app_env).lower() != environment.lower())
        return False

    def _get_extension_name(self) -> str:
        """
        Get the display name of the extension for logging purposes.

        Returns:
            String name of the extension
        """
        return "GCP Cloud Logging"

    def _get_middleware_config_key(self) -> str:
        """
        Get the configuration key used to override middleware settings.

        Returns:
            Configuration key name for middleware override
        """
        return "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE"

    def init_app(self, app: Flask) -> None:
        """
        Initialize the extension with a Flask application.

        Args:
            app: Flask application instance
        """
        # Call parent init_app first
        super().init_app(app)

        # Override log level with GCP-specific config if using default parameter
        if self._original_log_level == logging.INFO:  # Only if parameter was default
            gcp_log_level = self.config.get("GCP_LOG_LEVEL")
            if gcp_log_level is not None:
                self.log_level = gcp_log_level
