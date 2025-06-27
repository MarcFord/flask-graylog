import logging
from typing import Any, Callable, Optional, cast

from flask import Flask

try:
    from pygelf import GelfTcpHandler
except ImportError:
    GelfTcpHandler = None

from .base_extension import BaseLoggingExtension


class GraylogExtension(BaseLoggingExtension):
    """
    Flask extension for integrating with Graylog.

    This extension provides an easy-to-use interface for sending logs from a Flask application
    to a Graylog server.
    """

    def __init__(
        self,
        app: Optional[Flask] = None,
        get_current_user: Optional[Callable] = None,
        context_filter: Optional[logging.Filter] = None,
        log_formatter: Optional[logging.Formatter] = None,
        log_level: int = logging.INFO,
        additional_logs: Optional[list[str]] = None,
        enable_middleware: bool = True,
    ):
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

    def init_app(
        self,
        app: Flask,
        get_current_user: Optional[Callable] = None,
        context_filter: Optional[logging.Filter] = None,
        log_formatter: Optional[logging.Formatter] = None,
        log_level: int = logging.INFO,
        additional_logs: Optional[list[str]] = None,
        enable_middleware: Optional[bool] = None,
    ) -> None:
        """
        Initialize the extension with the given Flask application.

        :param app: The Flask application instance.
        """
        # Update instance attributes if provided
        if get_current_user:
            self.get_current_user = get_current_user
        if additional_logs:
            self.additional_logs = additional_logs
        if log_level != logging.INFO:  # Only update if explicitly changed from default
            self.log_level = log_level
        if log_formatter:
            self.log_formatter = log_formatter
        if context_filter:
            self.context_filter = context_filter
        if enable_middleware is not None:
            self.enable_middleware = enable_middleware

        # Call parent init_app which handles the common setup
        super().init_app(app)

    def _get_config_from_app(self) -> dict[str, Any]:
        """
        Retrieve configuration settings from the Flask application.

        :return: A dictionary of configuration settings.
        """
        if not self.app:
            raise RuntimeError("GraylogExtension must be initialized with a Flask app.")

        app_name = self.app.config.get("GRAYLOG_APP_NAME", self.app.name)

        return {
            "GRAYLOG_HOST": self.app.config.get("GRAYLOG_HOST", "localhost"),
            "GRAYLOG_PORT": self.app.config.get("GRAYLOG_PORT", 12201),
            "GRAYLOG_LOG_LEVEL": self.app.config.get("GRAYLOG_LOG_LEVEL", logging.INFO),
            "GRAYLOG_APP_NAME": app_name,
            "GRAYLOG_SERVICE_NAME": self.app.config.get("GRAYLOG_SERVICE_NAME", app_name),
            "GRAYLOG_ENVIRONMENT": self.app.config.get("GRAYLOG_ENVIRONMENT", "production"),
            "FLASK_REMOTE_LOGGING_ENVIRONMENT": self.app.config.get(
                "FLASK_REMOTE_LOGGING_ENVIRONMENT",
                self.app.config.get("GRAYLOG_ENVIRONMENT", "production"),  # Backward compatibility
            ),
            "GRAYLOG_EXTRA_FIELDS": self.app.config.get("GRAYLOG_EXTRA_FIELDS", True),
            "GRAYLOG_DEBUG": self.app.config.get("GRAYLOG_DEBUG", True),
            "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE": self.app.config.get(
                "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE", None
            ),
        }

    def _init_backend(self) -> None:
        """
        Initialize the Graylog backend.

        For Graylog, there's no special backend initialization needed.
        """
        pass

    def _create_log_handler(self) -> Optional[logging.Handler]:
        """
        Create the appropriate log handler for Graylog.

        Returns:
            GelfTcpHandler for production environment, StreamHandler otherwise
        """
        if self.app is None:
            return None

        # Flask compatibility: support both app.env (Flask 1.x) and config['ENV'] (Flask 2.0+)
        flask_env = self._get_flask_env()
        target_env = self.config.get("FLASK_REMOTE_LOGGING_ENVIRONMENT", "production")

        if str(flask_env).lower() == target_env.lower():
            if GelfTcpHandler is None:
                raise ImportError(
                    "pygelf is required for Graylog support. "
                    "Install it with: pip install flask-network-logging[graylog]"
                )

            return cast(
                logging.Handler,
                GelfTcpHandler(
                    host=self.config["GRAYLOG_HOST"],
                    port=self.config["GRAYLOG_PORT"],
                    debug=self.config["GRAYLOG_DEBUG"],
                    _app_name=self.config["GRAYLOG_APP_NAME"],
                    _service_name=self.config["GRAYLOG_SERVICE_NAME"],
                    _environment=self.config["GRAYLOG_ENVIRONMENT"],
                    include_extra_fields=self.config["GRAYLOG_EXTRA_FIELDS"],
                ),
            )
        else:
            # Use StreamHandler for non-production environments
            log_handler = logging.StreamHandler()
            log_handler.setFormatter(self.log_formatter)
            return log_handler

    def _should_skip_setup(self) -> bool:
        """
        Determine if logging setup should be skipped.

        For Graylog, we never skip setup - we just use different handlers
        based on the environment.

        Returns:
            False - Graylog extension always sets up logging
        """
        return False

    def _get_extension_name(self) -> str:
        """
        Get the display name of the extension.

        Returns:
            Display name for Graylog extension
        """
        return "Graylog"

    def _get_middleware_config_key(self) -> str:
        """
        Get the configuration key for middleware override.

        Returns:
            Configuration key name for middleware
        """
        return "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE"

    # Keep the old _setup_logging method for backward compatibility but mark as deprecated
    def _setup_logging(self) -> None:
        """
        Configures logging for the Flask application based on the provided configuration.

        .. deprecated::
            This method is now handled by the base class. Override _create_log_handler() instead.
        """
        # Delegate to parent implementation
        super()._setup_logging()
