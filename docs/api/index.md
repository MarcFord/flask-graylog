# API Reference

Complete API documentation for Flask Network Logging.

```{toctree}
:maxdepth: 2

extensions
filters
middleware
handlers
utilities
```

## Overview

Flask Network Logging provides a comprehensive API for integrating remote logging into Flask applications. The API is organized into several key modules:

### Core Extensions

The main extension classes for each logging backend:

- {class}`flask_remote_logging.GraylogExtension` - Graylog GELF logging
- {class}`flask_remote_logging.AWSLogExtension` - AWS CloudWatch Logs  
- {class}`flask_remote_logging.GCPLogExtension` - Google Cloud Logging
- {class}`flask_remote_logging.AzureLogExtension` - Azure Monitor Logs
- {class}`flask_remote_logging.IBMLogExtension` - IBM Cloud Logs
- {class}`flask_remote_logging.OCILogExtension` - Oracle Cloud Infrastructure

### Context Filters

Filters that add request context and metadata to log records:

- {class}`flask_remote_logging.FlaskRemoteLoggingContextFilter` - Request context filter

### Middleware

Automatic request/response logging components:

- {func}`flask_remote_logging.middleware.setup_middleware` - Configure middleware
- {func}`flask_remote_logging.middleware.before_request` - Request start handler  
- {func}`flask_remote_logging.middleware.after_request` - Request completion handler

### Custom Handlers

Logging handlers for each backend service:

- {class}`flask_remote_logging.aws_extension.CloudWatchHandler` - AWS CloudWatch handler
- {class}`flask_remote_logging.azure_extension.AzureMonitorHandler` - Azure handler
- {class}`flask_remote_logging.ibm_extension.IBMCloudLogHandler` - IBM handler

## Quick Reference

### Common Classes

```python
from flask_remote_logging import (
    GraylogExtension,           # Graylog integration
    AWSLogExtension,            # AWS CloudWatch
    GCPLogExtension,            # Google Cloud Logging
    AzureLogExtension,          # Azure Monitor
    IBMLogExtension,            # IBM Cloud Logs
    OCILogExtension,            # Oracle Cloud Infrastructure
    FlaskRemoteLoggingContextFilter,       # Request context filter
)
```

### Common Functions

```python
from flask_remote_logging.middleware import (
    setup_middleware,           # Configure automatic logging
    before_request,             # Request start handler
    after_request,              # Request completion handler
)
```

## API Conventions

### Parameter Naming

All API parameters follow consistent naming conventions:

- **`app`** - Flask application instance
- **`get_current_user`** - Function to retrieve user information
- **`log_level`** - Logging level (integer or string)
- **`additional_logs`** - List of additional logger names
- **`context_filter`** - Custom logging filter
- **`log_formatter`** - Custom log formatter
- **`enable_middleware`** - Enable/disable automatic middleware

### Configuration Keys

Configuration keys follow a consistent pattern:

- **`{BACKEND}_HOST`** - Service hostname
- **`{BACKEND}_PORT`** - Service port
- **`{BACKEND}_LEVEL`** - Log level
- **`{BACKEND}_ENVIRONMENT`** - Target environment
- **`FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE`** - Global middleware control

### Return Values

- **Extensions** - Return the extension instance for chaining
- **Middleware functions** - Return Flask response objects
- **Handlers** - Return None (log records are emitted)
- **Filters** - Return True (records are always processed)

## Type Annotations

Flask Network Logging is fully type-annotated. Import types for better IDE support:

```python
from typing import Optional, List, Callable, Dict, Any
from flask import Flask
from logging import Handler, Filter, Formatter

from flask_remote_logging import GraylogExtension

def setup_logging(
    app: Flask,
    get_user: Optional[Callable] = None,
    level: int = logging.INFO,
) -> GraylogExtension:
    return GraylogExtension(
        app=app,
        get_current_user=get_user,
        log_level=level,
    )
```

## Error Handling

All API methods include comprehensive error handling:

```python
try:
    graylog = GraylogExtension(app)
except ImportError:
    # Missing dependencies
    print("Install with: pip install flask-remote-logging[graylog]")
except ConnectionError:
    # Network/service issues  
    print("Check your Graylog server configuration")
except Exception as e:
    # Other errors
    print(f"Logging setup failed: {e}")
```

## Detailed API Documentation

Select a section for detailed API documentation:

- **[Extensions](extensions.md)** - Main extension classes
- **[Filters](filters.md)** - Context filters and custom filters  
- **[Middleware](middleware.md)** - Request/response middleware
- **[Handlers](handlers.md)** - Backend-specific log handlers
- **[Utilities](utilities.md)** - Helper functions and utilities
