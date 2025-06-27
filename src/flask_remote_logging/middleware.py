import time

from flask import Flask, Response, current_app, g, request


def setup_middleware(app: Flask) -> None:
    """Configure middleware to log each response"""
    app.before_request(before_request)
    app.after_request(after_request)


def before_request():
    """Middleware handler to record start time of each request"""
    # Record request start time, so we can get response time later
    g.flask_remote_logging = time.time()


def after_request(response: Response) -> Response:
    """Middleware helper to report each flask response to graylog"""
    # Calculate the elapsed time for this request
    elapsed = 0
    if hasattr(g, "flask_remote_logging"):
        elapsed = time.time() - g.flask_remote_logging
        elapsed = int(round(1000 * elapsed))

    # Extra metadata to include with the message
    extra = {
        "flask": {
            "endpoint": str(request.endpoint).lower(),
            "view_args": request.view_args,
        },
        "response": {
            "headers": dict(
                (key.replace("-", "_").lower(), value)
                for key, value in response.headers
                if key.lower() not in ("cookie",)
            ),
            "status_code": response.status_code,
            "time_ms": elapsed,
        },
        "request": {
            "content_length": request.environ.get("CONTENT_LENGTH"),
            "content_type": request.environ.get("CONTENT_TYPE"),
            "method": request.environ.get("REQUEST_METHOD"),
            "path_info": request.environ.get("PATH_INFO"),
            "headers": dict(
                (key[5:].replace("-", "_").lower(), value)
                for key, value in request.environ.items()
                if key.startswith("HTTP_") and key.lower() not in ("http_cookie",)
            ),
        },
    }

    message = 'Finishing request for "%s %s" from %s' % (request.method, request.url, extra.get("remote_addr", "-"))
    current_app.logger.info(message, extra=extra)

    # Always return the response
    return response
