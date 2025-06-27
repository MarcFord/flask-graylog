"""
flask_remote_logging.context_filter
---------------------------

This module provides a logging filter for Flask applications that enriches log records
with contextual information from the current request and environment. The filter is
designed to facilitate structured logging for remote logging systems like Graylog,
Google Cloud Logging, AWS CloudWatch Logs, and similar log aggregation platforms.

Features:
    - Adds request-specific data such as request ID, client IP, user agent, URL, and HTTP method.
    - Extracts and attaches user information if available.
    - Filters sensitive GET/POST parameters to avoid logging confidential data.
    - Enriches logs with host and environment details (hostname, OS, Python version).
    - Handles cases where no request context is present gracefully.

Classes:
    - FlaskRemoteLoggingContextFilter: A logging.Filter subclass that injects contextual data into log records.

Intended Usage:
    Attach FlaskRemoteLoggingContextFilter to Flask app loggers to automatically include rich context
    in all log messages, improving traceability and debugging in distributed environments.

"""

import logging
import platform
import pprint
import uuid
from typing import Any, Callable, Dict, Optional, cast

from flask import Request, g, has_request_context, request
from user_agents import parse


class FlaskRemoteLoggingContextFilter(logging.Filter):
    """
    A logging filter that adds context information to log records.

    This filter adds the Flask request context and any additional fields
    specified in the configuration to the log records. It's designed to work
    with multiple remote logging backends including Graylog, Google Cloud Logging,
    AWS CloudWatch Logs, and other structured logging systems.

    Note: Despite the name 'Graylog', this filter is used by all logging extensions
    in the flask-network-logging package. The name is kept for backward compatibility.
    Use FlaskRemoteLoggingContextFilter for clearer naming.
    """

    FILTER_FIELDS = (
        "card_number",
        "ccnum",
        "new_card-ccnum",
        "password",
        "password_confirm",
    )

    def __init__(self, *args: Any, get_current_user: Optional[Callable] = None, **kwargs: Any):
        """
        Initializes the context filter.

        Args:
            get_current_user (Optional[Callable], optional): A callable that returns the current user, if provided.
                                                            Defaults to None.
            *args: Variable length argument list for the superclass initializer.
            **kwargs: Arbitrary keyword arguments for the superclass initializer.
        """
        super().__init__(*args, **kwargs)
        self.__request: Optional[Request] = None
        self.__request_id: Optional[str] = None
        self.get_current_user: Optional[Callable] = get_current_user

    @property
    def request(self) -> Optional[Request]:
        """
        Returns the current Flask request object if available.

        If the internal request attribute is not set and a request context exists,
        it assigns the current Flask request to the internal attribute. Returns the
        stored request object or None if no request context is present.

        Returns:
            Optional[Request]: The current Flask request object, or None if not in a request context.
        """
        if self.__request is None and has_request_context():
            self.__request = cast(Request, request)
        return self.__request

    @property
    def request_id(self) -> Optional[str]:
        """
        Retrieves or generates a unique request ID for the current request context.

        The method attempts to obtain the request ID in the following order:
        1. If the Flask global `g` object has a `request_id` attribute, it is used.
        2. If the request headers contain "X-Request-ID", its value is used.
        3. If the request headers contain "Request-ID", its value is used.
        4. If the request headers contain "X-RequestId", its value is used.
        5. If none of the above are present, a new UUID4 hex string is generated.

        Returns:
            str: The unique request ID associated with the current request.
        """
        if self.__request_id is None and self.request:
            if hasattr(g, "request_id"):
                self.__request_id = g.request_id
            elif self.request.headers.get("X-Request-ID"):
                self.__request_id = self.request.headers.get("X-Request-ID")
            elif self.request.headers.get("Request-ID"):
                self.__request_id = self.request.headers.get("Request-ID")
            elif self.request.headers.get("X-RequestId"):
                self.__request_id = self.request.headers.get("X-RequestId")
            else:
                self.__request_id = uuid.uuid4().hex
        return str(self.__request_id) if self.__request_id else None

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter the log record to add context information.

        :param record: The log record to filter.
        :return: True if the record should be logged, False otherwise.
        """
        self._add_host_info(record)
        self._add_get_params(record)
        self._add_request_id(record)
        self._add_request_data(record)
        self._add_user_info(record)

        return True

    def _add_user_info(self, log_record: logging.LogRecord) -> None:
        """
        Adds user information to the provided log record if available.

        This method attempts to retrieve the current user by calling `self.get_current_user`.
        It supports user objects represented as either dictionaries or objects with attributes.
        The following user fields are extracted if present: 'id', 'uuid', 'username', and 'email'.
        Each extracted field is added to the `log_record` as an attribute, provided it does not already exist.

        Args:
            log_record (logging.LogRecord): The log record to which user information will be added.

        Notes:
            - If a user field value cannot be converted to a string, it will be skipped.
            - If `self.get_current_user` is not callable, no user information is added.
        """
        if callable(self.get_current_user):
            try:
                current_user = self.get_current_user()
            except Exception:
                # If get_current_user raises an exception, skip adding user info
                return

            user_info = {}
            if isinstance(current_user, dict):
                if "id" in current_user:
                    user_info["id"] = current_user["id"]
                if "uuid" in current_user:
                    user_info["uuid"] = current_user["uuid"]
                if "username" in current_user:
                    user_info["username"] = current_user["username"]
                if "email" in current_user:
                    user_info["email"] = current_user["email"]
            elif isinstance(current_user, object):
                if hasattr(current_user, "id"):
                    user_info["id"] = current_user.id
                if hasattr(current_user, "uuid"):
                    user_info["uuid"] = current_user.uuid
                if hasattr(current_user, "username"):
                    user_info["username"] = current_user.username
                if hasattr(current_user, "email"):
                    user_info["email"] = current_user.email
            for key, value in user_info.items():
                if not hasattr(log_record, key):
                    try:
                        value_str = str(value)
                    except (TypeError, ValueError, UnicodeError, Exception):  # nosec B110
                        # Skip values that cannot be converted to string safely
                        continue
                    setattr(log_record, key, value_str)

    def _add_host_info(self, log_record: logging.LogRecord) -> None:
        """
        Adds host information to the provided log record.

        This method enriches the log record with the hostname, operating system,
        and Python version of the server where the application is running.

        Args:
            log_record (logging.LogRecord): The log record to be enriched with host information.
        """
        log_record.hostname = platform.node()
        log_record.os = platform.system()
        log_record.os_version = platform.release()
        log_record.python_version = platform.python_version()
        log_record.python_implementation = platform.python_implementation()

    def _add_get_params(self, log_record: logging.LogRecord) -> None:
        """
        Adds HTTP GET parameters from the current request to the provided log record.

        If a request is present, this method formats the filtered GET parameters and attaches them to the log record as
        the 'get_params' attribute. It also sets each filtered parameter as an attribute on the log record, unless the
        attribute already exists. If no request is present, sets the 'no_request' attribute on the log record to "True"
        if it is not already set.

        Args:
            log_record (logging.LogRecord): The log record to which GET parameters will be added.

        Raises:
            Exception: Silently ignores any exception that occurs while setting attributes on the log record.
        """
        if self.request:
            try:
                pp = pprint.PrettyPrinter(indent=4)
                log_record.get_params = pp.pformat(self.__filter_param_fields(self.request.values.to_dict()))
                try:
                    for key, value in self.__filter_param_fields(self.request.values.to_dict()).items():
                        if not hasattr(log_record, key):
                            setattr(log_record, key, value)
                except (KeyError, AttributeError, TypeError):  # nosec B110
                    # Skip if parameter processing fails
                    pass
            except (AttributeError, TypeError):  # nosec B110
                # Handle cases where request.values or to_dict() are missing/broken
                log_record.get_params = "Error accessing request parameters"
        else:
            log_record.get_params = "No request context"
            log_record.no_request = "True" if not hasattr(log_record, "no_request") else log_record.no_request

    def _add_request_id(self, log_record: logging.LogRecord) -> None:
        """
        Adds a unique request ID to the provided log record.

        If a request context is available, this method enriches the log record with a unique request ID.
        If no request context is present, it marks the log record accordingly.

        Args:
            log_record (logging.LogRecord): The log record to be enriched with the request ID.
        """
        if self.request_id:
            log_record.request_id = self.request_id
        else:
            log_record.no_request = "True" if not hasattr(log_record, "no_request") else log_record.no_request

    def _add_request_data(self, log_record: logging.LogRecord) -> None:
        """
        Adds HTTP request-related data to the provided log record.

        If a request context is available, this method enriches the log record with client IP address,
        user agent details, operating system, browser information, mobile status, request URL, and HTTP method.
        If no request context is present, it marks the log record accordingly.

        Args:
            log_record (logging.LogRecord): The log record to be enriched with request data.
        """
        if self.request:
            client_data = self.__get_client_data()
            log_record.client_ip_address = self.__get_ip_address()
            log_record.user_agent = request.user_agent.string
            log_record.user_os = str(client_data.get("os", "Unknown"))
            log_record.user_browser = str(client_data.get("browser", {}).get("name", "Unknown"))
            log_record.user_browser_version = str(client_data.get("browser", {}).get("version", "Unknown"))
            log_record.user_mobile = str(client_data.get("mobile", False))
            log_record.url = str(self.request.url)
            log_record.request_method = str(self.request.method)
        else:
            log_record.no_request = "True"

    def __get_ip_address(self) -> Optional[str]:
        """
        Retrieve the client's IP address from the request object.

        This method checks various headers and environment variables commonly used to pass the client's
        IP address through proxies and load balancers, in the following order of precedence:
        1. "HTTP_X_FORWARDED_FOR" from the WSGI environment
        2. "REMOTE_ADDR" from the WSGI environment
        3. "HTTP_X_REAL_IP" from the WSGI environment
        4. "HTTP_X_FORWARDED" from the WSGI environment
        5. "X-Forwarded-For" from the request headers
        6. "X-Real-IP" from the request headers
        7. "X-Forwarded" from the request headers
        8. The request's `remote_addr` attribute

        Returns:
            Optional[str]: The detected IP address as a string, or None if it cannot be determined.
        """
        if self.request:
            if self.request.environ.get("HTTP_X_FORWARDED_FOR", None):
                ip_address = self.request.environ.get("HTTP_X_FORWARDED_FOR")
            elif self.request.environ.get("REMOTE_ADDR", None):
                ip_address = self.request.environ.get("REMOTE_ADDR")
            elif self.request.environ.get("HTTP_X_REAL_IP", None):
                ip_address = self.request.environ.get("HTTP_X_REAL_IP")
            elif self.request.environ.get("HTTP_X_FORWARDED", None):
                ip_address = self.request.environ.get("HTTP_X_FORWARDED")
            elif self.request.headers.get("X-Forwarded-For", None):
                ip_address = self.request.headers.get("X-Forwarded-For")
            elif self.request.headers.get("X-Real-IP", None):
                ip_address = self.request.headers.get("X-Real-IP")
            elif self.request.headers.get("X-Forwarded", None):
                ip_address = self.request.headers.get("X-Forwarded")
            else:
                ip_address = self.request.remote_addr
        else:
            ip_address = None

        return str(ip_address) if ip_address else None

    def __get_client_data(self) -> Dict[str, Any]:
        """
        Retrieve client-related data from the current request.

        Returns:
            Dict[str, Any]: A dictionary containing the client's IP address, browser information (name and version),
            operating system, and whether the client is using a mobile device. Returns an empty dictionary if there is
            no request.
        """
        if self.request is None:
            return {}
        user_agent = parse(request.user_agent.string)
        return {
            "ip_address": self._get_client_ip(),
            "browser": {
                "name": user_agent.browser.family,
                "version": user_agent.browser.version[0] if user_agent.browser.version else None,
            },
            "os": user_agent.os.family,
            "mobile": user_agent.is_mobile,
        }

    def _get_client_ip(self) -> Optional[str]:
        """
        Retrieve the client's IP address from the request object.

        Returns:
            Optional[str]: The detected IP address as a string, or None if it cannot be determined.
        """
        return self.__get_ip_address()

    def __filter_param_fields(self, params_dict: dict) -> dict:
        """
        Filters sensitive fields in the given dictionary by replacing their
        values with asterisks.

        Args:
            params_dict (dict): The dictionary containing parameters to be
                filtered.

        Returns:
            dict: A new dictionary with sensitive fields' values replaced by
                asterisks.
        """
        filtered_dict = {}
        for param, value in params_dict.items():
            filtered_dict[param] = "*" * len(str(value)) if param in self.FILTER_FIELDS else value
        return filtered_dict
