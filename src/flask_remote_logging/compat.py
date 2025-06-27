"""
Flask version compatibility utilities.

This module provides helper functions to handle differences between
Flask versions, particularly around environment configuration.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask


def set_flask_env(app: "Flask", environment: str) -> None:
    """
    Set Flask environment in a version-compatible way.

    Args:
        app: Flask application instance
        environment: Environment name (e.g., 'development', 'production')
    """
    # Always set config['ENV'] for Flask 2.x+
    app.config["ENV"] = environment

    # Set app.env for Flask 1.x compatibility if the attribute exists and is writable
    if hasattr(app, "env"):
        try:
            # Use setattr to avoid static analysis issues
            setattr(app, "env", environment)
        except (AttributeError, TypeError):
            # Some Flask versions may have read-only env attribute
            pass


def get_flask_env(app: "Flask | None") -> str:
    """
    Get Flask environment in a version-compatible way.

    Args:
        app: Flask application instance

    Returns:
        The current Flask environment (e.g., 'development', 'production')
    """
    if app is None:
        return "production"

    # Try Flask 1.x app.env first, then Flask 2.0+ config['ENV']
    # Use getattr to safely access potentially missing attribute
    env_attr = getattr(app, "env", None)
    if env_attr is not None and isinstance(env_attr, str):
        return str(env_attr)  # Explicit cast to satisfy mypy

    # Fall back to config['ENV'] and ensure it's a string
    env_config = app.config.get("ENV", "production")
    return str(env_config)
