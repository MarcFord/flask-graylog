"""
AWS CloudWatch Logs Extension for Flask Network Logging

This module provides the AWSLogExtension class for sending Flask application logs
to AWS CloudWatch Logs. It integrates with the flask-network-logging package to
provide comprehensive logging capabilities for AWS environments.
"""

import logging
import os
from typing import Any, Callable, Dict, List, Optional

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    boto3 = None
    ClientError = Exception
    NoCredentialsError = Exception

from .context_filter import GraylogContextFilter


class AWSLogExtension:
    """
    Flask extension for sending logs to AWS CloudWatch Logs.

    This extension provides integration between Flask applications and AWS CloudWatch Logs,
    allowing for centralized logging in AWS environments. It supports automatic request
    context logging, custom fields, and configurable log levels.

    Features:
    - Automatic AWS CloudWatch Logs integration
    - Request context logging with user information
    - Configurable log levels and filtering
    - Custom field support
    - Environment-based configuration
    - Error handling and fallback logging

    Example:
        ```python
        from flask import Flask
        from flask_network_logging import AWSLogExtension

        app = Flask(__name__)
        app.config.update({
            'AWS_REGION': 'us-east-1',
            'AWS_LOG_GROUP': '/aws/lambda/my-function',
            'AWS_LOG_STREAM': 'my-stream',
            'AWS_LOG_LEVEL': 'INFO'
        })

        aws_log = AWSLogExtension(app)
        aws_log._setup_logging()

        # The extension uses a reusable context filter that works
        # with all flask-network-logging backends (Graylog, GCP, AWS)
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
        Initialize the AWS CloudWatch Logs extension.

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
        self.cloudwatch_client = None
        self.log_group = None
        self.log_stream = None

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

        # Initialize AWS CloudWatch client if boto3 is available
        if boto3:
            try:
                self._init_cloudwatch_client()
            except Exception as e:
                app.logger.warning(f"Failed to initialize AWS CloudWatch client: {e}")

    def _get_config_from_app(self) -> Dict[str, Any]:
        """
        Extract AWS CloudWatch configuration from Flask app config.

        Returns:
            Dictionary containing AWS CloudWatch configuration
        """
        if not self.app:
            return {}

        return {
            "AWS_REGION": self.app.config.get("AWS_REGION", os.getenv("AWS_REGION", "us-east-1")),
            "AWS_ACCESS_KEY_ID": self.app.config.get("AWS_ACCESS_KEY_ID", os.getenv("AWS_ACCESS_KEY_ID")),
            "AWS_SECRET_ACCESS_KEY": self.app.config.get("AWS_SECRET_ACCESS_KEY", os.getenv("AWS_SECRET_ACCESS_KEY")),
            "AWS_LOG_GROUP": self.app.config.get("AWS_LOG_GROUP", os.getenv("AWS_LOG_GROUP")),
            "AWS_LOG_STREAM": self.app.config.get("AWS_LOG_STREAM", os.getenv("AWS_LOG_STREAM")),
            "AWS_LOG_LEVEL": self.app.config.get("AWS_LOG_LEVEL", os.getenv("AWS_LOG_LEVEL", "INFO")),
            "AWS_ENVIRONMENT": self.app.config.get("AWS_ENVIRONMENT", os.getenv("AWS_ENVIRONMENT", "development")),
            "AWS_CREATE_LOG_GROUP": self.app.config.get(
                "AWS_CREATE_LOG_GROUP", os.getenv("AWS_CREATE_LOG_GROUP", "true").lower() == "true"
            ),
            "AWS_CREATE_LOG_STREAM": self.app.config.get(
                "AWS_CREATE_LOG_STREAM", os.getenv("AWS_CREATE_LOG_STREAM", "true").lower() == "true"
            ),
        }

    def _init_cloudwatch_client(self):
        """Initialize the AWS CloudWatch Logs client."""
        if not boto3:
            raise ImportError(
                "boto3 is required for AWS CloudWatch Logs support. "
                "Install it with: pip install flask-network-logging[aws]"
            )

        try:
            # Create CloudWatch Logs client
            session_kwargs = {"region_name": self.config.get("AWS_REGION", "us-east-1")}

            # Add credentials if provided
            aws_access_key = self.config.get("AWS_ACCESS_KEY_ID")
            aws_secret_key = self.config.get("AWS_SECRET_ACCESS_KEY")

            if aws_access_key and aws_secret_key:
                session_kwargs["aws_access_key_id"] = aws_access_key
                session_kwargs["aws_secret_access_key"] = aws_secret_key

            session = boto3.Session(**session_kwargs)
            self.cloudwatch_client = session.client("logs")

            # Set log group and stream names
            self.log_group = self.config.get("AWS_LOG_GROUP")
            self.log_stream = self.config.get("AWS_LOG_STREAM")

        except (NoCredentialsError, ClientError) as e:
            if self.app:
                self.app.logger.warning(f"AWS CloudWatch Logs initialization failed: {e}")
            self.cloudwatch_client = None

    def _ensure_log_group_exists(self):
        """Ensure the CloudWatch log group exists, create if it doesn't."""
        if not self.cloudwatch_client or not self.log_group:
            return

        try:
            self.cloudwatch_client.describe_log_groups(logGroupNamePrefix=self.log_group)
        except ClientError:
            try:
                self.cloudwatch_client.create_log_group(logGroupName=self.log_group)
                if self.app:
                    self.app.logger.info(f"Created CloudWatch log group: {self.log_group}")
            except ClientError as e:
                if self.app:
                    self.app.logger.warning(f"Failed to create log group {self.log_group}: {e}")

    def _ensure_log_stream_exists(self):
        """Ensure the CloudWatch log stream exists, create if it doesn't."""
        if not self.cloudwatch_client or not self.log_group or not self.log_stream:
            return

        try:
            self.cloudwatch_client.describe_log_streams(
                logGroupName=self.log_group, logStreamNamePrefix=self.log_stream
            )
        except ClientError:
            try:
                self.cloudwatch_client.create_log_stream(logGroupName=self.log_group, logStreamName=self.log_stream)
                if self.app:
                    self.app.logger.info(f"Created CloudWatch log stream: {self.log_stream}")
            except ClientError as e:
                if self.app:
                    self.app.logger.warning(f"Failed to create log stream {self.log_stream}: {e}")

    def _setup_logging(self):
        """
        Set up logging configuration for AWS CloudWatch Logs.

        This method configures the Flask application's logging to send logs to
        AWS CloudWatch Logs when in appropriate environments.
        """
        if not self.app:
            return

        # Re-read config in case it was updated after initialization
        self.config = self._get_config_from_app()

        # Check if we should set up CloudWatch logging
        environment = self.config.get("AWS_ENVIRONMENT", "development")

        # Only set up CloudWatch logging in AWS environments or when explicitly configured
        if environment not in ["aws", "production"] and not self.config.get("AWS_LOG_GROUP"):
            if environment == "development":
                self.app.logger.info("AWS CloudWatch Logs: Skipping setup in development environment")
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

        self.app.logger.info("AWS CloudWatch Logs extension initialized successfully")

    def _configure_logger(self, logger: logging.Logger, level: int):
        """
        Configure a specific logger with AWS CloudWatch handler.

        Args:
            logger: Logger instance to configure
            level: Log level to set
        """
        # Set log level
        logger.setLevel(level)

        # Create CloudWatch handler if client is available
        if self.cloudwatch_client and self.log_group and self.log_stream:
            try:
                # Ensure log group and stream exist
                if self.config.get("AWS_CREATE_LOG_GROUP", True):
                    self._ensure_log_group_exists()

                if self.config.get("AWS_CREATE_LOG_STREAM", True):
                    self._ensure_log_stream_exists()

                cloudwatch_handler = CloudWatchHandler(
                    client=self.cloudwatch_client, log_group=self.log_group, log_stream=self.log_stream
                )
                cloudwatch_handler.setLevel(level)
                cloudwatch_handler.setFormatter(self.log_formatter)

                if self.context_filter:
                    cloudwatch_handler.addFilter(self.context_filter)

                logger.addHandler(cloudwatch_handler)

            except Exception as e:
                if self.app:
                    self.app.logger.warning(f"Failed to add CloudWatch handler: {e}")

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


class CloudWatchHandler(logging.Handler):
    """
    Custom logging handler for AWS CloudWatch Logs.

    This handler sends log records to AWS CloudWatch Logs using the boto3 client.
    It handles batching and error recovery for reliable log delivery.
    """

    def __init__(self, client, log_group: str, log_stream: str):
        """
        Initialize the CloudWatch handler.

        Args:
            client: boto3 CloudWatch Logs client
            log_group: CloudWatch log group name
            log_stream: CloudWatch log stream name
        """
        super().__init__()
        self.client = client
        self.log_group = log_group
        self.log_stream = log_stream
        self.sequence_token = None

    def emit(self, record: logging.LogRecord):
        """
        Emit a log record to CloudWatch Logs.

        Args:
            record: Log record to emit
        """
        try:
            # Format the log message
            message = self.format(record)

            # Prepare log event
            log_event = {"timestamp": int(record.created * 1000), "message": message}  # CloudWatch expects milliseconds

            # Send to CloudWatch
            self._send_log_event(log_event)

        except Exception as e:
            # Don't let logging errors break the application
            self.handleError(record)

    def _send_log_event(self, log_event: Dict[str, Any]):
        """
        Send a single log event to CloudWatch Logs.

        Args:
            log_event: Log event dictionary
        """
        try:
            kwargs = {"logGroupName": self.log_group, "logStreamName": self.log_stream, "logEvents": [log_event]}

            # Include sequence token if we have one
            if self.sequence_token:
                kwargs["sequenceToken"] = self.sequence_token

            response = self.client.put_log_events(**kwargs)

            # Update sequence token for next request
            self.sequence_token = response.get("nextSequenceToken")

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")

            if error_code == "InvalidSequenceTokenException":
                # Reset sequence token and retry
                self.sequence_token = None
                self._send_log_event(log_event)
            else:
                raise
