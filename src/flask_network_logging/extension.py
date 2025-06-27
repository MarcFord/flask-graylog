import logging
from typing import Any, Callable, Optional

from flask import Flask

try:
    from pygelf import GelfTcpHandler
except ImportError:
    GelfTcpHandler = None

from .context_filter import GraylogContextFilter
from .middleware import setup_middleware


class GraylogExtension:
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
        self.context_filter: Optional[logging.Filter] = context_filter
        self.log_formatter: Optional[logging.Formatter] = log_formatter
        self.log_level: int = log_level
        self.additional_logs: Optional[list[str]] = additional_logs
        self.app: Optional[Flask] = None
        self.get_current_user: Optional[Callable] = get_current_user
        self.config: dict[str, Any] = {}
        self._logging_setup: bool = False
        self.enable_middleware: bool = enable_middleware

        if app is not None:
            self.init_app(
                app,
                get_current_user=get_current_user,
                context_filter=context_filter,
                log_formatter=log_formatter,
                log_level=log_level,
                additional_logs=additional_logs,
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
        enable_middleware: bool = True,
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
        self.enable_middleware = enable_middleware

        # Additional initialization logic can be added here.
        self.config = self._get_config_from_app()
        if not self.context_filter and not context_filter:
            self.context_filter = GraylogContextFilter(get_current_user=get_current_user or self.get_current_user)
        elif context_filter:
            self.context_filter = context_filter

        if self.config.get("FLASK_NETWORK_LOGGING_ENABLE_MIDDLEWARE") is not None:
            self.enable_middleware = self.config.get("FLASK_NETWORK_LOGGING_ENABLE_MIDDLEWARE", enable_middleware)

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
            self.log_level = self.config.get("GRAYLOG_LOG_LEVEL", self.log_level)

        # Set up logging automatically
        self._setup_logging()

    def _setup_logging(self) -> None:
        """
        Configures logging for the Flask application based on the provided configuration.

        If the application's environment matches the configured Graylog environment,
        sets up a GELF TCP handler for logging to Graylog. Otherwise, uses a standard
        stream handler with the specified log formatter.

        The log handler's level is set according to the configured log level. If a context
        filter is provided, it is added to the log handler and any additional loggers.

        The handler is attached to the Flask app's logger and to any additional loggers
        specified in the configuration.

        Raises:
            RuntimeError: If the extension is not initialized with a Flask app.
        """
        if not self.app:
            raise RuntimeError("GraylogExtension must be initialized with a Flask app.")

        # Prevent duplicate setup
        if self._logging_setup:
            return

        self._logging_setup = True

        if str(self.app.env).lower() == self.app.config.get("GRAYLOG_ENVIRONMENT", "production").lower():
            if GelfTcpHandler is None:
                raise ImportError(
                    "pygelf is required for Graylog support. "
                    "Install it with: pip install flask-network-logging[graylog]"
                )

            log_handler = GelfTcpHandler(
                host=self.config["GRAYLOG_HOST"],
                port=self.config["GRAYLOG_PORT"],
                debug=self.config["GRAYLOG_DEBUG"],
                _app_name=self.config["GRAYLOG_APP_NAME"],
                _service_name=self.config["GRAYLOG_SERVICE_NAME"],
                _environment=self.config["GRAYLOG_ENVIRONMENT"],
                include_extra_fields=self.config["GRAYLOG_EXTRA_FIELDS"],
            )
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

        if self.enable_middleware:
            setup_middleware(self.app)

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
            "GRAYLOG_EXTRA_FIELDS": self.app.config.get("GRAYLOG_EXTRA_FIELDS", True),
            "GRAYLOG_DEBUG": self.app.config.get("GRAYLOG_DEBUG", True),
            "FLASK_NETWORK_LOGGING_ENABLE_MIDDLEWARE": self.app.config.get("FLASK_NETWORK_LOGGING_ENABLE_MIDDLEWARE", None),
        }
