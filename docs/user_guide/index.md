# User Guide

This comprehensive guide covers everything you need to know about using Flask Network Logging effectively in your applications.

## What You'll Learn

The user guide is organized into focused sections:

```{toctree}
:maxdepth: 2

backends
middleware 
factory_pattern
advanced_config
best_practices
troubleshooting
```

## Quick Navigation

### Getting Started
- **[Backend Selection](backends.md)** - Choose the right logging backend for your needs
- **[Middleware System](middleware.md)** - Understand automatic request/response logging
- **[Factory Pattern](factory_pattern.md)** - Use with Flask application factories

### Advanced Topics
- **[Advanced Configuration](advanced_config.md)** - Custom filters, formatters, and complex setups
- **[Best Practices](best_practices.md)** - Production tips and performance optimization
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## Core Concepts

### Extension Architecture

Flask Network Logging uses a modular architecture:

```python
from flask_remote_logging import GraylogExtension

# Each backend is a separate extension class
graylog = GraylogExtension(app)   # For Graylog
aws_log = AWSLogExtension(app)    # For AWS CloudWatch  
gcp_log = GCPLogExtension(app)    # For Google Cloud Logging
```

### Automatic Setup

All extensions feature automatic setup - no manual configuration needed:

```python
# Old way (deprecated):
# extension = GraylogExtension(app)
# extension._setup_logging()

# New way (automatic):
extension = GraylogExtension(app)  # Logging is ready!
```

### Environment-Based Configuration

Extensions respect Flask's environment settings:

```python
# Development environment
app.config['GRAYLOG_ENVIRONMENT'] = 'development'

# Production environment  
app.config['GRAYLOG_ENVIRONMENT'] = 'production'

# Logs are only sent when Flask env matches logging env
```

### Request Context Integration

Automatic integration with Flask's request context:

```python
@app.route('/users/<int:user_id>')
def get_user(user_id):
    # Automatic context includes:
    # - Request method, path, headers
    # - User information (if available)
    # - Response timing and status
    app.logger.info(f"Retrieving user {user_id}")
    return jsonify(user_data)
```

## Common Patterns

### Single Backend Setup

Most applications use a single logging backend:

```python
from flask import Flask
from flask_remote_logging import GraylogExtension

app = Flask(__name__)
app.config.update({
    'GRAYLOG_HOST': 'logs.company.com',
    'GRAYLOG_PORT': 12201,
    'GRAYLOG_ENVIRONMENT': 'production',
})

graylog = GraylogExtension(app)
```

### Multi-Backend Setup

For complex deployments, you can use multiple backends:

```python
from flask_remote_logging import (
    GraylogExtension, 
    AWSLogExtension, 
    GCPLogExtension
)

# Configure multiple backends
graylog = GraylogExtension(app)    # Primary logging
aws_log = AWSLogExtension(app)     # Cloud-specific logs
gcp_log = GCPLogExtension(app)     # Analytics pipeline
```

### Conditional Backend Selection

Choose backends based on environment:

```python
import os
from flask_remote_logging import GraylogExtension, AWSLogExtension

if os.getenv('DEPLOYMENT_ENV') == 'aws':
    logger = AWSLogExtension(app)
elif os.getenv('DEPLOYMENT_ENV') == 'on-premise':
    logger = GraylogExtension(app)
```

## Configuration Philosophy

### Convention Over Configuration

Flask Network Logging follows Flask's philosophy:

- **Sensible defaults** - Works out of the box with minimal config
- **Easy customization** - Override only what you need
- **Clear naming** - Configuration keys are predictable and consistent

### Environment Variables

All configuration can be set via environment variables:

```bash
# Instead of app.config['GRAYLOG_HOST']
export GRAYLOG_HOST=logs.company.com
export GRAYLOG_PORT=12201
export GRAYLOG_ENVIRONMENT=production
```

### Runtime Configuration

Configuration is evaluated at runtime:

```python
# Configuration is read when extension initializes
app.config['GRAYLOG_HOST'] = get_logging_host()  # Dynamic
graylog = GraylogExtension(app)  # Uses current config
```

## Development vs Production

### Development Setup

```python
# Minimal configuration for development
app.config.update({
    'GRAYLOG_HOST': 'localhost',
    'GRAYLOG_LEVEL': 'DEBUG',
    'GRAYLOG_ENVIRONMENT': 'development',
})
```

### Production Setup

```python
# Production configuration with security and performance
app.config.update({
    'GRAYLOG_HOST': os.getenv('GRAYLOG_HOST'),
    'GRAYLOG_PORT': int(os.getenv('GRAYLOG_PORT', 12201)),
    'GRAYLOG_LEVEL': 'INFO',
    'GRAYLOG_ENVIRONMENT': 'production',
    'GRAYLOG_EXTRA_FIELDS': True,
    'FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE': True,
})
```

## Next Steps

Choose your path based on your needs:

1. **New to the library?** → Start with [Backend Selection](backends.md)
2. **Want automatic logging?** → Read about [Middleware](middleware.md)  
3. **Using app factories?** → Check [Factory Pattern](factory_pattern.md)
4. **Need custom setup?** → See [Advanced Configuration](advanced_config.md)
5. **Going to production?** → Review [Best Practices](best_practices.md)
6. **Having issues?** → Visit [Troubleshooting](troubleshooting.md)
