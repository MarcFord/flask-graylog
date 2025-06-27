"""Tests for the AWSLogExtension class."""

import logging
from unittest.mock import MagicMock, Mock, patch

import pytest
from flask import Flask

from flask_remote_logging import AWSLogExtension
from flask_remote_logging.context_filter import FlaskRemoteLoggingContextFilter


class TestAWSLogExtension:
    """Test cases for the AWSLogExtension class."""

    def test_init_without_app(self):
        """Test initialization without a Flask app."""
        extension = AWSLogExtension()

        assert extension.app is None
        assert extension.context_filter is None
        assert extension.log_formatter is None
        assert extension.log_level == logging.INFO
        assert extension.additional_logs == []
        assert extension.get_current_user is None
        assert extension.config == {}
        assert extension.cloudwatch_client is None
        assert extension.log_group is None
        assert extension.log_stream is None

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_init_with_app(self, mock_boto3, app):
        """Test initialization with a Flask app."""
        # Mock boto3 session and client
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_client

        extension = AWSLogExtension(app=app)

        assert extension.app is app
        assert extension.config is not None
        assert "AWS_REGION" in extension.config

    def test_init_with_parameters(self, app, mock_get_current_user):
        """Test initialization with custom parameters."""
        custom_filter = Mock(spec=logging.Filter)
        custom_formatter = Mock(spec=logging.Formatter)

        with patch("flask_remote_logging.aws_extension.boto3"):
            extension = AWSLogExtension(
                app=app,
                get_current_user=mock_get_current_user,
                log_level=logging.DEBUG,
                additional_logs=["test.logger"],
                context_filter=custom_filter,
                log_formatter=custom_formatter,
            )

            assert extension.app is app
            assert extension.get_current_user is mock_get_current_user
            assert extension.log_level == logging.DEBUG
            assert extension.additional_logs == ["test.logger"]
            assert extension.context_filter is custom_filter
            assert extension.log_formatter is custom_formatter

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_init_app_method(self, mock_boto3, app):
        """Test the init_app method."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_client

        extension = AWSLogExtension()
        extension.init_app(app)

        assert extension.app is app
        assert extension.config is not None

    def test_get_config_from_app_without_app(self):
        """Test _get_config_from_app without an app."""
        extension = AWSLogExtension()
        config = extension._get_config_from_app()

        assert config == {}

    def test_get_config_from_app_with_defaults(self, app):
        """Test _get_config_from_app with default values."""
        extension = AWSLogExtension()
        extension.app = app
        config = extension._get_config_from_app()

        assert config["AWS_REGION"] == "us-east-1"
        assert config["AWS_LOG_LEVEL"] == "INFO"
        assert config["AWS_ENVIRONMENT"] == "development"
        assert config["AWS_CREATE_LOG_GROUP"] is True
        assert config["AWS_CREATE_LOG_STREAM"] is True

    def test_get_config_from_app_with_custom_values(self, app):
        """Test _get_config_from_app with custom configuration values."""
        app.config.update(
            {
                "AWS_REGION": "us-west-2",
                "AWS_LOG_GROUP": "/aws/lambda/test-function",
                "AWS_LOG_STREAM": "test-stream",
                "AWS_LOG_LEVEL": "DEBUG",
                "AWS_ENVIRONMENT": "production",
                "AWS_CREATE_LOG_GROUP": False,
            }
        )

        extension = AWSLogExtension()
        extension.app = app
        config = extension._get_config_from_app()

        assert config["AWS_REGION"] == "us-west-2"
        assert config["AWS_LOG_GROUP"] == "/aws/lambda/test-function"
        assert config["AWS_LOG_STREAM"] == "test-stream"
        assert config["AWS_LOG_LEVEL"] == "DEBUG"
        assert config["AWS_ENVIRONMENT"] == "production"
        assert config["AWS_CREATE_LOG_GROUP"] is False

    def test_setup_logging_without_app(self):
        """Test _setup_logging without an app."""
        extension = AWSLogExtension()

        # Should not raise an exception
        extension._setup_logging()

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_setup_logging_with_aws_environment(self, mock_boto3, app):
        """Test _setup_logging in AWS environment."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_client

        app.config.update(
            {"AWS_ENVIRONMENT": "aws", "AWS_LOG_GROUP": "/aws/lambda/test", "AWS_LOG_STREAM": "test-stream"}
        )

        extension = AWSLogExtension(app=app)
        extension._setup_logging()

        # Should have created context filter
        assert extension.context_filter is not None
        assert isinstance(extension.context_filter, FlaskRemoteLoggingContextFilter)

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_setup_logging_with_development_environment(self, mock_boto3, app):
        """Test _setup_logging in development environment."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_client

        app.config.update({"AWS_ENVIRONMENT": "development"})

        with patch.object(app.logger, "info") as mock_info:
            extension = AWSLogExtension(app=app)
            # The setup happens automatically during init, so check for the expected call
            mock_info.assert_called_with("AWS CloudWatch Logs: Skipping setup in test environment")

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_init_cloudwatch_client_with_credentials(self, mock_boto3, app):
        """Test CloudWatch client initialization with explicit credentials."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_client

        app.config.update(
            {
                "AWS_REGION": "us-west-2",
                "AWS_ACCESS_KEY_ID": "test-key",
                "AWS_SECRET_ACCESS_KEY": "test-secret",
                "AWS_LOG_GROUP": "/aws/lambda/test",
                "AWS_LOG_STREAM": "test-stream",
            }
        )

        extension = AWSLogExtension(app=app)

        # Verify Session was called with correct parameters
        mock_boto3.Session.assert_called_with(
            region_name="us-west-2", aws_access_key_id="test-key", aws_secret_access_key="test-secret"
        )

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_init_cloudwatch_client_without_credentials(self, mock_boto3, app):
        """Test CloudWatch client initialization without explicit credentials."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_client

        app.config.update(
            {"AWS_REGION": "eu-west-1", "AWS_LOG_GROUP": "/aws/lambda/test", "AWS_LOG_STREAM": "test-stream"}
        )

        extension = AWSLogExtension(app=app)

        # Verify Session was called with only region
        mock_boto3.Session.assert_called_with(region_name="eu-west-1")

    def test_init_cloudwatch_client_without_boto3(self, app):
        """Test CloudWatch client initialization when boto3 is not available."""
        with patch("flask_remote_logging.aws_extension.boto3", None):
            extension = AWSLogExtension(app=app)
            assert extension.cloudwatch_client is None

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_ensure_log_group_exists_success(self, mock_boto3, app):
        """Test ensuring log group exists when it already exists."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_client

        # Mock successful describe_log_groups call
        mock_client.describe_log_groups.return_value = {"logGroups": []}

        app.config.update({"AWS_LOG_GROUP": "/aws/lambda/test", "AWS_ENVIRONMENT": "development"})

        extension = AWSLogExtension()
        extension.init_app(app)
        # Reset mock call counts since init_app may call it
        mock_client.reset_mock()

        extension._ensure_log_group_exists()

        mock_client.describe_log_groups.assert_called_once_with(logGroupNamePrefix="/aws/lambda/test")
        mock_client.create_log_group.assert_not_called()

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_ensure_log_group_exists_create(self, mock_boto3, app):
        """Test ensuring log group exists when it needs to be created."""
        from botocore.exceptions import ClientError

        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_client

        # Mock describe_log_groups to raise ClientError (not found)
        mock_client.describe_log_groups.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}}, "DescribeLogGroups"
        )

        app.config.update({"AWS_LOG_GROUP": "/aws/lambda/test", "AWS_ENVIRONMENT": "development"})

        extension = AWSLogExtension()
        extension.init_app(app)
        # Reset mock call counts since init_app may call it
        mock_client.reset_mock()
        mock_client.describe_log_groups.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}}, "DescribeLogGroups"
        )

        with patch.object(app.logger, "info") as mock_info:
            extension._ensure_log_group_exists()
            mock_client.create_log_group.assert_called_once_with(logGroupName="/aws/lambda/test")
            mock_info.assert_called_with("Created CloudWatch log group: /aws/lambda/test")

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_ensure_log_stream_exists_success(self, mock_boto3, app):
        """Test ensuring log stream exists when it already exists."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_client

        # Mock successful describe_log_streams call
        mock_client.describe_log_streams.return_value = {"logStreams": []}

        app.config.update({"AWS_LOG_GROUP": "/aws/lambda/test", "AWS_LOG_STREAM": "test-stream"})

        extension = AWSLogExtension(app=app)

        # Reset mock to only track calls made after automatic setup
        mock_client.describe_log_streams.reset_mock()
        extension._ensure_log_stream_exists()

        mock_client.describe_log_streams.assert_called_once_with(
            logGroupName="/aws/lambda/test", logStreamNamePrefix="test-stream"
        )
        mock_client.create_log_stream.assert_not_called()

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_setup_logging_with_context_filter(self, mock_boto3, app):
        """Test _setup_logging with custom context filter."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_client

        custom_filter = Mock(spec=logging.Filter)

        app.config.update({"AWS_ENVIRONMENT": "production", "AWS_LOG_GROUP": "/aws/lambda/test"})

        extension = AWSLogExtension(app=app, context_filter=custom_filter)
        extension._setup_logging()

        assert extension.context_filter is custom_filter

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_setup_logging_with_additional_logs(self, mock_boto3, app):
        """Test _setup_logging with additional loggers."""
        mock_session = MagicMock()
        mock_client = MagicMock()
        mock_boto3.Session.return_value = mock_session
        mock_session.client.return_value = mock_client

        app.config.update({"AWS_ENVIRONMENT": "production", "AWS_LOG_GROUP": "/aws/lambda/test"})

        with patch("logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # The setup happens automatically during init
            extension = AWSLogExtension(app=app, additional_logs=["test.logger", "another.logger"])

            # Should have called getLogger for each additional logger during automatic setup
            assert mock_get_logger.call_count == 2

    def test_context_filter_creation(self, app, mock_get_current_user):
        """Test that context filter is created correctly."""
        with patch("flask_remote_logging.aws_extension.boto3"):
            # AWS extension should create default context filter if none provided
            extension = AWSLogExtension(app=app, get_current_user=mock_get_current_user)

            # The AWS extension should create a default context filter during init
            assert extension.context_filter is not None
            assert isinstance(extension.context_filter, FlaskRemoteLoggingContextFilter)

    def test_log_formatter_creation(self, app):
        """Test that log formatter is created correctly."""
        with patch("flask_remote_logging.aws_extension.boto3"):
            # AWS extension should create default log formatter if none provided
            extension = AWSLogExtension(app=app)

            # The AWS extension should create a default log formatter during init
            assert extension.log_formatter is not None
            assert isinstance(extension.log_formatter, logging.Formatter)

    def test_log_level_parameter_override(self, app):
        """Test that log level parameter overrides config."""
        with patch("flask_remote_logging.aws_extension.boto3"):
            app.config.update(
                {"AWS_LOG_LEVEL": "INFO", "AWS_ENVIRONMENT": "production", "AWS_LOG_GROUP": "/aws/lambda/test"}
            )

            extension = AWSLogExtension(app=app, log_level=logging.DEBUG)
            # The extension should use the parameter value, not config
            assert extension.log_level == logging.DEBUG


class TestCloudWatchHandler:
    """Test cases for the CloudWatchHandler class."""

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_cloudwatch_handler_init(self, mock_boto3):
        """Test CloudWatchHandler initialization."""
        from flask_remote_logging.aws_extension import CloudWatchHandler

        mock_client = Mock()
        handler = CloudWatchHandler(client=mock_client, log_group="/aws/lambda/test", log_stream="test-stream")

        assert handler.client is mock_client
        assert handler.log_group == "/aws/lambda/test"
        assert handler.log_stream == "test-stream"
        assert handler.sequence_token is None

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_cloudwatch_handler_emit(self, mock_boto3):
        """Test CloudWatchHandler emit method."""
        from flask_remote_logging.aws_extension import CloudWatchHandler

        mock_client = Mock()
        mock_client.put_log_events.return_value = {"nextSequenceToken": "token123"}

        handler = CloudWatchHandler(client=mock_client, log_group="/aws/lambda/test", log_stream="test-stream")

        # Create a log record
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0, msg="Test message", args=(), exc_info=None
        )

        handler.emit(record)

        # Verify put_log_events was called
        mock_client.put_log_events.assert_called_once()
        args, kwargs = mock_client.put_log_events.call_args

        assert kwargs["logGroupName"] == "/aws/lambda/test"
        assert kwargs["logStreamName"] == "test-stream"
        assert len(kwargs["logEvents"]) == 1
        assert kwargs["logEvents"][0]["message"] == "Test message"

        # Verify sequence token was updated
        assert handler.sequence_token == "token123"

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_cloudwatch_handler_emit_with_sequence_token(self, mock_boto3):
        """Test CloudWatchHandler emit method with existing sequence token."""
        from botocore.exceptions import ClientError

        from flask_remote_logging.aws_extension import CloudWatchHandler

        mock_client = Mock()
        mock_client.put_log_events.return_value = {"nextSequenceToken": "token456"}

        handler = CloudWatchHandler(client=mock_client, log_group="/aws/lambda/test", log_stream="test-stream")
        handler.sequence_token = "existing_token"

        # Create a log record
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0, msg="Test message", args=(), exc_info=None
        )

        handler.emit(record)

        # Verify put_log_events was called with sequence token
        mock_client.put_log_events.assert_called_once()
        args, kwargs = mock_client.put_log_events.call_args

        assert kwargs["sequenceToken"] == "existing_token"
        assert handler.sequence_token == "token456"

    @patch("flask_remote_logging.aws_extension.boto3")
    def test_cloudwatch_handler_emit_invalid_sequence_token(self, mock_boto3):
        """Test CloudWatchHandler emit method with invalid sequence token."""
        from botocore.exceptions import ClientError

        from flask_remote_logging.aws_extension import CloudWatchHandler

        mock_client = Mock()
        # First call fails with InvalidSequenceTokenException
        # Second call succeeds
        mock_client.put_log_events.side_effect = [
            ClientError({"Error": {"Code": "InvalidSequenceTokenException"}}, "PutLogEvents"),
            {"nextSequenceToken": "new_token"},
        ]

        handler = CloudWatchHandler(client=mock_client, log_group="/aws/lambda/test", log_stream="test-stream")
        handler.sequence_token = "invalid_token"

        # Create a log record
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0, msg="Test message", args=(), exc_info=None
        )

        handler.emit(record)

        # Verify put_log_events was called twice (retry after invalid token)
        assert mock_client.put_log_events.call_count == 2
        assert handler.sequence_token == "new_token"
