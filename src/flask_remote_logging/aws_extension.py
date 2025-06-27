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

from flask import Flask

from .base_extension import BaseLoggingExtension


class AWSLogExtension(BaseLoggingExtension):
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
        from flask_remote_logging import AWSLogExtension

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
        app: Optional[Flask] = None,
        get_current_user: Optional[Callable] = None,
        log_level: int = logging.INFO,
        additional_logs: Optional[List[str]] = None,
        context_filter: Optional[logging.Filter] = None,
        log_formatter: Optional[logging.Formatter] = None,
        enable_middleware: bool = True,
    ):
        """
        Initialize the AWS CloudWatch Logs extension.

        Args:
            app: Flask application instance
            get_current_user: Function to retrieve current user information
            log_level: Logging level (default: INFO)
            additional_logs: List of additional logger names to configure
            context_filter: Custom logging filter (if None, FlaskRemoteLoggingContextFilter is used)
            log_formatter: Custom log formatter
            enable_middleware: Whether to enable request/response middleware (default: True)
        """
        # AWS-specific attributes
        self.cloudwatch_client = None
        self.log_group = None
        self.log_stream = None

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

        # AWS extension expects additional_logs to be [] if None
        if self.additional_logs is None:
            self.additional_logs = []

    # Abstract method implementations

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
            "FLASK_REMOTE_LOGGING_ENVIRONMENT": self.app.config.get(
                "FLASK_REMOTE_LOGGING_ENVIRONMENT",
                self.app.config.get(
                    "AWS_ENVIRONMENT", os.getenv("AWS_ENVIRONMENT", "development")
                ),  # Backward compatibility
            ),
            "AWS_CREATE_LOG_GROUP": self.app.config.get(
                "AWS_CREATE_LOG_GROUP", os.getenv("AWS_CREATE_LOG_GROUP", "true").lower() == "true"
            ),
            "AWS_CREATE_LOG_STREAM": self.app.config.get(
                "AWS_CREATE_LOG_STREAM", os.getenv("AWS_CREATE_LOG_STREAM", "true").lower() == "true"
            ),
            "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE": self.app.config.get(
                "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE", None
            ),
        }

    def _init_backend(self) -> None:
        """Initialize the AWS CloudWatch backend."""
        # Initialize AWS CloudWatch client if boto3 is available
        if boto3:
            try:
                self._init_cloudwatch_client()
            except Exception as e:
                if self.app:
                    self.app.logger.warning(f"Failed to initialize AWS CloudWatch client: {e}")

    def _create_log_handler(self) -> Optional[logging.Handler]:
        """Create the appropriate log handler for AWS CloudWatch."""
        # Only set up CloudWatch logging in AWS environments or when explicitly configured
        environment = self.config.get("FLASK_REMOTE_LOGGING_ENVIRONMENT", "development")

        if environment in ["aws", "production"] or self.config.get("AWS_LOG_GROUP"):
            if self.cloudwatch_client and self.log_group:
                # Ensure log group and stream exist
                if self.config.get("AWS_CREATE_LOG_GROUP", True):
                    self._ensure_log_group_exists()
                if self.config.get("AWS_CREATE_LOG_STREAM", True) and self.log_stream:
                    self._ensure_log_stream_exists()

                # Create a simple CloudWatch handler (placeholder)
                handler = logging.StreamHandler()
                handler.setFormatter(
                    self.log_formatter or logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                )
                return handler
            else:
                # Fallback to stream handler if CloudWatch not properly configured
                return logging.StreamHandler()
        else:
            # Return None to skip setup
            return None

    def _should_skip_setup(self) -> bool:
        """
        Determine if setup should be skipped based on environment and configuration.

        AWS extension skips setup unless:
        - Environment is 'aws' or 'production', OR
        - AWS_LOG_GROUP is explicitly configured
        """
        environment = self.config.get("FLASK_REMOTE_LOGGING_ENVIRONMENT", "development")
        return environment not in ["aws", "production"] and not self.config.get("AWS_LOG_GROUP")

    def _get_extension_name(self) -> str:
        """Get the display name of the extension."""
        return "AWS CloudWatch Logs"

    def _get_middleware_config_key(self) -> str:
        """Get the configuration key for middleware override."""
        return "FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE"

    # AWS-specific helper methods

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

        except Exception:
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

        except Exception as e:
            # Handle both ClientError and general exceptions
            if hasattr(e, "response"):
                response = getattr(e, "response", {})
                if "Error" in response:
                    error_code = response.get("Error", {}).get("Code")
                    if error_code == "InvalidSequenceTokenException":
                        # Reset sequence token and retry
                        self.sequence_token = None
                        self._send_log_event(log_event)
                    else:
                        raise
                else:
                    raise
            else:
                raise
