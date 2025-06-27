"""
Base extension class for Flask network logging extensions.

This module provides a common base class that all logging extensions inherit from,
reducing code duplication and ensuring consistent behavior across all extensions.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from flask import Flask

from .compat import get_flask_env
from .context_filter import FlaskRemoteLoggingContextFilter
from .middleware import setup_middleware


class BaseLoggingExtension(ABC):
    """
    Abstract base class for Flask network logging extensions.

    This class provides common functionality shared across all logging extensions
    including initialization, configuration management, and basic setup patterns.

    Concrete extensions should inherit from this class and implement the required
    abstract methods for their specific logging backend.
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
        Initialize the logging extension.

        Args:
            app: Flask application instance
            get_current_user: Function to retrieve current user information
            log_level: Logging level (default: INFO)
            additional_logs: List of additional logger names to configure
            context_filter: Custom logging filter (if None, FlaskRemoteLoggingContextFilter is used)
            log_formatter: Custom log formatter
            enable_middleware: Whether to enable request/response middleware (default: True)
        """
        # Core attributes
        self.app: Optional[Flask] = app
        self.get_current_user: Optional[Callable] = get_current_user
        self.log_level: int = log_level
        self.additional_logs: Optional[List[str]] = additional_logs
        self.context_filter: Optional[logging.Filter] = context_filter
        self.log_formatter: Optional[logging.Formatter] = log_formatter
        self.enable_middleware: bool = enable_middleware

        # Configuration and state
        self.config: Dict[str, Any] = {}
        self._logging_setup: bool = False

        # Initialize with app if provided
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """
        Initialize the extension with a Flask application.

        This method handles common initialization steps and calls extension-specific
        setup methods.

        Args:
            app: Flask application instance
        """
        self.app = app

        # Load configuration
        self.config = self._get_config_from_app()

        # Create default context filter if none provided
        if not self.context_filter:
            self.context_filter = FlaskRemoteLoggingContextFilter(get_current_user=self.get_current_user)

        # Create default log formatter if none provided
        if not self.log_formatter:
            self.log_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(hostname)s: %(message)s "
                "[in %(pathname)s:%(lineno)d]"
                "params: %(get_params)s"
            )

        # Apply middleware configuration override if present
        middleware_config_key = self._get_middleware_config_key()
        if self.config.get(middleware_config_key) is not None:
            self.enable_middleware = self.config.get(middleware_config_key, self.enable_middleware)

        # Apply log level from config if not explicitly overridden
        config_log_level_key = f"{self._get_extension_name().upper().replace(' ', '_')}_LOG_LEVEL"
        config_log_level = self.config.get(config_log_level_key)
        if config_log_level is not None and self.log_level == logging.INFO:  # Only apply if still using default
            self.log_level = config_log_level

        # Perform extension-specific initialization
        self._init_backend()

        # Set up logging and middleware
        self._setup_logging()

    def _setup_logging(self) -> None:
        """
        Configure logging for the Flask application.

        This method handles the common logging setup pattern including handler creation,
        filter attachment, and middleware setup. Extensions can override this for
        custom behavior.
        """
        if not self.app:
            # If no app is configured, simply return without error (backward compatibility)
            return

        # Prevent duplicate setup
        if self._logging_setup:
            return

        self._logging_setup = True

        # Check if we should skip setup based on environment
        if self._should_skip_setup():
            if hasattr(self.app, "logger"):
                skip_reason = self._get_skip_reason()
                self.app.logger.info(f"{self._get_extension_name()}: {skip_reason}")
            return

        # Create the appropriate log handler
        log_handler = self._create_log_handler()

        if log_handler:
            # Configure the handler
            log_handler.setLevel(self.log_level)

            if self.context_filter:
                log_handler.addFilter(self.context_filter)

            # Add handler to app logger
            if hasattr(self.app, "logger"):
                self.app.logger.addHandler(log_handler)
                self.app.logger.setLevel(self.log_level)

                # Configure additional loggers
                self._configure_additional_loggers(log_handler)

        # Set up middleware if enabled
        if self.enable_middleware:
            setup_middleware(self.app)

        # Log successful initialization
        if hasattr(self.app, "logger"):
            self.app.logger.info(f"{self._get_extension_name()} extension initialized successfully")

    def _configure_additional_loggers(self, log_handler: logging.Handler) -> None:
        """
        Configure additional loggers with the same handler and filters.

        Args:
            log_handler: The logging handler to attach to additional loggers
        """
        if self.additional_logs:
            for log_name in self.additional_logs:
                additional_logger = logging.getLogger(log_name)
                additional_logger.setLevel(self.log_level)
                additional_logger.addHandler(log_handler)
                if self.context_filter:
                    additional_logger.addFilter(self.context_filter)

    def _configure_logger(self, logger: logging.Logger, level: int) -> None:
        """
        Configure a logger with the extension's handler and level.

        This is a common pattern used by extensions for configuring loggers.

        Args:
            logger: The logger to configure
            level: The logging level to set
        """
        if hasattr(self, "_handler") and self._handler:
            logger.addHandler(self._handler)
            logger.setLevel(level)
            if self.context_filter:
                logger.addFilter(self.context_filter)

    def _get_flask_env(self) -> str:
        """
        Get Flask environment in a version-compatible way.

        This is a convenience method that delegates to the centralized
        compatibility function.

        Returns:
            The current Flask environment (e.g., 'development', 'production')
        """
        return get_flask_env(self.app)

    # Abstract methods that subclasses must implement

    @abstractmethod
    def _get_config_from_app(self) -> Dict[str, Any]:
        """
        Extract configuration from the Flask application.

        Each extension implements this to load its specific configuration keys.

        Returns:
            Dictionary containing the extension's configuration
        """
        pass

    @abstractmethod
    def _init_backend(self) -> None:
        """
        Initialize the logging backend (AWS, Azure, GCP, etc.).

        This method is called during init_app() and should handle any
        backend-specific initialization like client creation, authentication, etc.
        """
        pass

    @abstractmethod
    def _create_log_handler(self) -> Optional[logging.Handler]:
        """
        Create the appropriate log handler for this extension.

        Returns:
            A logging.Handler instance configured for the specific backend,
            or None if setup should be skipped
        """
        pass

    def _should_skip_setup(self) -> bool:
        """
        Determine if logging setup should be skipped based on environment or config.

        This method checks if the current Flask environment matches the configured
        target environment for remote logging. Extensions can override this for
        custom logic, but most should use this default implementation.

        Returns:
            True if setup should be skipped, False otherwise
        """
        if not self.app:
            return True

        # Get the target environment for this extension
        target_environment = self.config.get("FLASK_REMOTE_LOGGING_ENVIRONMENT", "production")

        # Get the current Flask environment
        current_environment = self._get_flask_env()

        # Skip setup if environments don't match
        return str(current_environment).lower() != str(target_environment).lower()

    @abstractmethod
    def _get_extension_name(self) -> str:
        """
        Get the display name of the extension for logging purposes.

        Returns:
            String name of the extension (e.g., "AWS CloudWatch Logs", "Graylog")
        """
        pass

    @abstractmethod
    def _get_middleware_config_key(self) -> str:
        """
        Get the configuration key used to override middleware settings.

        Returns:
            Configuration key name for middleware override
        """
        pass

    def _get_skip_reason(self) -> str:
        """
        Get the reason why setup is being skipped.

        This default implementation returns a message about the current environment.
        Extensions can override this method if they need custom skip reason logic.

        Returns:
            Human-readable reason for skipping setup
        """
        if self.app:
            flask_env = self._get_flask_env()
            return f"Skipping setup in {flask_env} environment"
        return "Skipping setup (no app configured)"
