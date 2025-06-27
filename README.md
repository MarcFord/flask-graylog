# flask-remote-logging

[![CI](https://github.com/MarcFord/flask-remote-logging/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/MarcFord/flask-remote-logging/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/MarcFord/flask-remote-logging/branch/main/graph/badge.svg)](https://codecov.io/gh/MarcFord/flask-remote-logging)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/MarcFord/flask-remote-logging/blob/main/LICENSE)

A Flask extension for sending application logs to remote logging services including Graylog via GELF (Graylog Extended Log Format), Google Cloud Logging, AWS CloudWatch Logs, Azure Monitor Logs, IBM Cloud Logs, and Oracle Cloud Infrastructure Logging.

> **📊 Badge Status**: The CI badge shows the latest build status. The codecov badge will update once coverage reports are uploaded to codecov.io. PyPI badges will appear after the first release.

## Features

- 🚀 Easy Flask integration with multiple logging backends
- 📝 Automatic request context logging
- 🔧 Configurable log levels and filtering
- 🌍 Environment-based configuration
- 🏷️ Custom field support
- 🔒 Production-ready with comprehensive testing
- 🐍 Python 3.9+ support
- 📚 Comprehensive documentation

## Documentation

The full documentation for this library is available in the `docs/` directory and can be built using:

```bash
./build_docs.sh
```

This script creates a Python 3.9 virtual environment (needed due to compatibility issues with Python 3.13+) and builds the HTML documentation, which you can then view in your browser.

The docs cover:
- Detailed API documentation
- Integration guides for all supported logging backends
- Advanced configuration options
- Best practices for production environments
- 📡 Support for Graylog via GELF
- ☁️ Support for Google Cloud Logging
- 🚀 Support for AWS CloudWatch Logs
- 📊 Support for Azure Monitor Logs
- 🔵 Support for IBM Cloud Logs
- 🟠 Support for Oracle Cloud Infrastructure Logging

## Installation

### Basic Installation

Install the core package without any logging backend dependencies:

```bash
pip install flask-remote-logging
```

### Backend-Specific Installation

Install only the dependencies you need for your specific logging backend:

**For Graylog support:**
```bash
pip install flask-remote-logging[graylog]
```

**For Google Cloud Logging support:**
```bash
pip install flask-remote-logging[gcp]
```

**For AWS CloudWatch Logs support:**
```bash
pip install flask-remote-logging[aws]
```

**For Azure Monitor Logs support:**
```bash
pip install flask-remote-logging[azure]
```

**For IBM Cloud Logs support:**
```bash
pip install flask-remote-logging[ibm]
```

**For Oracle Cloud Infrastructure Logging support:**
```bash
pip install flask-remote-logging[oci]
```

**For multiple backends:**
```bash
# Install specific backends
pip install flask-remote-logging[graylog,aws,oci]

# Or install all backends
pip install flask-remote-logging[all]
```

### Why Optional Dependencies?

The optional dependencies approach provides several benefits:

- **📦 Smaller footprint**: Install only the dependencies you actually need
- **🚀 Faster installation**: Reduced package download and installation time
- **🐳 Smaller Docker images**: Especially important for containerized applications
- **🔒 Reduced security surface**: Fewer dependencies mean fewer potential vulnerabilities
- **📊 Better dependency management**: Avoid conflicts with unused logging backends
- **💰 Lower resource usage**: Particularly beneficial in serverless environments

The core package includes only Flask and essential utilities. Backend-specific dependencies (like `boto3`, `google-cloud-logging`, `pygelf`, `requests`) are installed only when you explicitly request them.

## Quick Start

### Graylog Integration

```python
from flask import Flask
from flask_remote_logging import GraylogExtension

app = Flask(__name__)

# Configure Graylog
app.config.update({
    'GRAYLOG_HOST': 'your-graylog-server.com',
    'GRAYLOG_PORT': 12201,
    'GRAYLOG_LEVEL': 'INFO',
    'FLASK_REMOTE_LOGGING_ENVIRONMENT': 'production'  # Unified environment key
})

# Initialize extension (logging setup is automatic)
graylog = GraylogExtension(app)

@app.route('/')
def hello():
    app.logger.info("Hello world endpoint accessed")
    return "Hello, World!"

if __name__ == '__main__':
    app.run()
```

### Google Cloud Logging Integration

```python
from flask import Flask
from flask_remote_logging import GCPLogExtension

app = Flask(__name__)

# Configure Google Cloud Logging
app.config.update({
    'GCP_PROJECT_ID': 'your-gcp-project-id',
    'GCP_LOG_NAME': 'flask-app',
    'GCP_LOG_LEVEL': 'INFO',
    'FLASK_REMOTE_LOGGING_ENVIRONMENT': 'production'  # Unified environment key
})

# Initialize extension (logging setup is automatic)
gcp_log = GCPLogExtension(app)

@app.route('/')
def hello():
    app.logger.info("Hello world endpoint accessed")
    return "Hello, World!"

if __name__ == '__main__':
    app.run()
```

### AWS CloudWatch Logs Integration

```python
from flask import Flask
from flask_remote_logging import AWSLogExtension

app = Flask(__name__)

# Configure AWS CloudWatch Logs
app.config.update({
    'AWS_REGION': 'us-east-1',
    'AWS_LOG_GROUP': '/flask-app/logs',
    'AWS_LOG_STREAM': 'app-stream',
    'AWS_LOG_LEVEL': 'INFO',
    'FLASK_REMOTE_LOGGING_ENVIRONMENT': 'production'  # Unified environment key
})

# Initialize extension (logging setup is automatic)
aws_log = AWSLogExtension(app)

@app.route('/')
def hello():
    app.logger.info("Hello world endpoint accessed")
    return "Hello, World!"

if __name__ == '__main__':
    app.run()
```

### Azure Monitor Logs Integration

```python
from flask import Flask
from flask_remote_logging import AzureLogExtension

app = Flask(__name__)

# Configure Azure Monitor Logs
app.config.update({
    'AZURE_WORKSPACE_ID': 'your-workspace-id',
    'AZURE_WORKSPACE_KEY': 'your-workspace-key',
    'AZURE_LOG_TYPE': 'FlaskAppLogs',
    'AZURE_LOG_LEVEL': 'INFO',
    'FLASK_REMOTE_LOGGING_ENVIRONMENT': 'production'  # Unified environment key
})

# Initialize extension (logging setup is automatic)
azure_log = AzureLogExtension(app)

@app.route('/')
def hello():
    app.logger.info("Hello world endpoint accessed")
    return "Hello, World!"

if __name__ == '__main__':
    app.run()
```

### IBM Cloud Logs Integration

```python
from flask import Flask
from flask_remote_logging import IBMLogExtension

app = Flask(__name__)

# Configure IBM Cloud Logs
app.config.update({
    'IBM_INGESTION_KEY': 'your-ingestion-key',
    'IBM_HOSTNAME': 'your-hostname',
    'IBM_APP_NAME': 'your-app-name',
    'IBM_ENV': 'production',
    'IBM_LOG_LEVEL': 'INFO',
    'FLASK_REMOTE_LOGGING_ENVIRONMENT': 'production'  # Unified environment key
})

# Initialize extension (logging setup is automatic)
ibm_log = IBMLogExtension(app)

@app.route('/')
def hello():
    app.logger.info("Hello world endpoint accessed")
    return "Hello, World!"

if __name__ == '__main__':
    app.run()
```

### Oracle Cloud Infrastructure Logging Integration

```python
from flask import Flask
from flask_remote_logging import OCILogExtension

app = Flask(__name__)

# Configure OCI Logging
app.config.update({
    'OCI_CONFIG_PROFILE': 'DEFAULT',
    'OCI_LOG_ID': 'ocid1.log.oc1...',
    'OCI_SOURCE': 'your-app-name',
    'OCI_LOG_LEVEL': 'INFO',
    'FLASK_REMOTE_LOGGING_ENVIRONMENT': 'production'  # Unified environment key
})

# Initialize extension (logging setup is automatic)
oci_log = OCILogExtension(app)

@app.route('/')
def hello():
    app.logger.info("Hello world endpoint accessed")
    return "Hello, World!"

if __name__ == '__main__':
    app.run()
```

### Unified Environment Configuration

As of version 2.0, flask-remote-logging supports a unified environment configuration key across all backends for consistency and easier management:

```python
app.config.update({
    # Unified environment configuration (recommended)
    'FLASK_REMOTE_LOGGING_ENVIRONMENT': 'production',
    
    # Backend-specific configuration
    'GRAYLOG_HOST': 'your-graylog-server.com',
    'GRAYLOG_PORT': 12201,
})
```

#### Migration from Backend-Specific Environment Keys

The old backend-specific environment keys (`GRAYLOG_ENVIRONMENT`, `AWS_ENVIRONMENT`, etc.) are still supported for backward compatibility, but the new unified key takes precedence:

```python
# Old way (still supported)
app.config.update({
    'GRAYLOG_ENVIRONMENT': 'production',  # Backend-specific
    'AWS_ENVIRONMENT': 'production',      # Backend-specific
})

# New unified way (recommended)
app.config.update({
    'FLASK_REMOTE_LOGGING_ENVIRONMENT': 'production',  # Works for all backends
})

# Mixed configuration (unified key takes precedence)
app.config.update({
    'FLASK_REMOTE_LOGGING_ENVIRONMENT': 'production',  # Used by all extensions
    'GRAYLOG_ENVIRONMENT': 'development',              # Ignored (fallback only)
})
```

**Benefits of the unified approach:**
- 🔧 **Consistent configuration** across all logging backends
- 🚀 **Easier multi-backend setup** with single environment setting
- 📝 **Simplified configuration management** in deployment environments
- 🔄 **Full backward compatibility** with existing configurations

### Advanced Configuration

### Middleware Control

By default, all logging extensions enable request/response middleware that automatically logs HTTP requests and responses. You can disable this middleware if you prefer to handle logging manually:

```python
from flask import Flask
from flask_remote_logging import GraylogExtension

app = Flask(__name__)
app.config.update({
    'GRAYLOG_HOST': 'your-graylog-server.com',
    'GRAYLOG_PORT': 12201,
})

# Initialize without middleware
graylog = GraylogExtension(app, enable_middleware=False)

@app.route('/')
def hello():
    # Manual logging without automatic request/response logging
    app.logger.info("Hello endpoint called manually")
    return "Hello, World!"
```

You can also control middleware via configuration:

```python
app.config.update({
    'GRAYLOG_HOST': 'your-graylog-server.com',
    'GRAYLOG_PORT': 12201,
    'FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE': False  # Disables middleware
})

# This will respect the config setting
graylog = GraylogExtension(app)
```

### Factory Pattern Support

The extensions support Flask's application factory pattern:

```python
from flask import Flask
from flask_remote_logging import GraylogExtension

# Create extension instance
graylog = GraylogExtension()

def create_app():
    app = Flask(__name__)
    app.config.update({
        'GRAYLOG_HOST': 'your-graylog-server.com',
        'GRAYLOG_PORT': 12201,
    })
    
    # Initialize with app
    graylog.init_app(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
```

## Migration Guide

### Upgrading from v1.x to v2.x

Version 2.0 introduces several improvements for consistency and ease of use. All changes are backward compatible.

#### Context Filter Changes

**v1.x (multiple aliases):**
```python
from flask_remote_logging import GraylogContextFilter, FRLContextFilter
# Multiple class names were available
```

**v2.x (single canonical class):**
```python
from flask_remote_logging import FlaskRemoteLoggingContextFilter
# Single canonical class name for consistency
```

The old aliases still work but are deprecated. Update your imports to use the new canonical class name.

#### Environment Configuration Changes

**v1.x (backend-specific keys):**
```python
app.config.update({
    'GRAYLOG_ENVIRONMENT': 'production',
    'AWS_ENVIRONMENT': 'production', 
    'AZURE_ENVIRONMENT': 'production',
    # Different keys for each backend
})
```

**v2.x (unified key with fallback):**
```python
app.config.update({
    # Recommended: Single unified key for all backends
    'FLASK_REMOTE_LOGGING_ENVIRONMENT': 'production',
    
    # Legacy keys still work for backward compatibility
    # 'GRAYLOG_ENVIRONMENT': 'production',  # Fallback only
})
```

**Migration steps:**
1. Update imports to use `FlaskRemoteLoggingContextFilter`
2. Replace backend-specific environment keys with `FLASK_REMOTE_LOGGING_ENVIRONMENT`
3. Test your application - old configuration should still work during transition
4. Remove legacy configuration keys once migration is complete

## Examples

Check out the comprehensive example application in the [`examples/`](examples/) directory:

- **Full Flask application** with complete Graylog integration
- **Multiple endpoints** demonstrating different log scenarios
- **Error handling** and performance monitoring
- **Docker Compose setup** for local Graylog testing
- **Ready-to-run scripts** for quick testing

```bash
cd examples/
./run_example.sh  # Complete setup with Graylog + Flask
```

## Compatibility

### Flask Version Support

This package is compatible with **Flask 1.4.4** and higher, including Flask 2.x and Flask 3.x.

Key compatibility features:
- **Environment Detection**: Automatically handles differences between Flask 1.x (`app.env`) and Flask 2.x+ (`app.config['ENV']`)
- **Configuration**: Works seamlessly with both old and new Flask configuration patterns
- **Testing**: Thoroughly tested across Flask versions to ensure compatibility

### Flask Version Utilities

The package provides compatibility utilities that you can use in your own code:

```python
from flask_remote_logging import get_flask_env, set_flask_env

# Get Flask environment in a version-compatible way
env = get_flask_env(app)  # Works with Flask 1.x and 2.x+

# Set Flask environment in a version-compatible way  
set_flask_env(app, 'production')  # Works with Flask 1.x and 2.x+
```

These utilities handle the differences between Flask versions automatically, so your code works regardless of the Flask version being used.

### Python Version Support

- **Python 3.9+**: Fully supported and tested
- **Python 3.13**: Compatible with latest Python releases

## Configuration

### Graylog Configuration

| Configuration Key | Description | Default |
|-------------------|-------------|---------|
| `GRAYLOG_HOST` | Graylog server hostname | `localhost` |
| `GRAYLOG_PORT` | Graylog GELF UDP port | `12201` |
| `GRAYLOG_LEVEL` | Minimum log level | `WARNING` |
| `FLASK_REMOTE_LOGGING_ENVIRONMENT` | **Unified environment key** - Environment where logs should be sent | `production` |
| `GRAYLOG_ENVIRONMENT` | *(Deprecated)* Legacy environment key - use `FLASK_REMOTE_LOGGING_ENVIRONMENT` instead | `development` |
| `GRAYLOG_EXTRA_FIELDS` | True to allow extra fields, False if not | True |
| `GRAYLOG_APP_NAME` | Name of the application sending logs | `app.name` |
| `GRAYLOG_SERVICE_NAME` | Name of the service sending logs. Useful if you have an application that is made up of multiple services | `app.name` |
| `FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE` | Enable/disable automatic request/response middleware | `True` |

### Google Cloud Logging Configuration

| Configuration Key | Description | Default |
|-------------------|-------------|---------|
| `GCP_PROJECT_ID` | Google Cloud Project ID | Required |
| `GCP_CREDENTIALS_PATH` | Path to service account JSON file (optional if using default credentials) | `None` |
| `GCP_LOG_NAME` | Name of the log in Cloud Logging | `flask-app` |
| `GCP_LOG_LEVEL` | Minimum log level | `WARNING` |
| `FLASK_REMOTE_LOGGING_ENVIRONMENT` | **Unified environment key** - Environment where logs should be sent | `production` |
| `GCP_ENVIRONMENT` | *(Deprecated)* Legacy environment key - use `FLASK_REMOTE_LOGGING_ENVIRONMENT` instead | `production` |
| `GCP_APP_NAME` | Name of the application sending logs | `app.name` |
| `GCP_SERVICE_NAME` | Name of the service sending logs | `app.name` |
| `FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE` | Enable/disable automatic request/response middleware | `True` |

### AWS CloudWatch Logs Configuration

| Configuration Key | Description | Default |
|-------------------|-------------|---------|
| `AWS_REGION` | AWS region for CloudWatch Logs | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key (optional if using IAM roles/profiles) | `None` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key (optional if using IAM roles/profiles) | `None` |
| `AWS_LOG_GROUP` | CloudWatch log group name | `/flask-app/logs` |
| `AWS_LOG_STREAM` | CloudWatch log stream name | `app-stream` |
| `AWS_LOG_LEVEL` | Minimum log level | `WARNING` |
| `FLASK_REMOTE_LOGGING_ENVIRONMENT` | **Unified environment key** - Environment where logs should be sent | `production` |
| `AWS_ENVIRONMENT` | *(Deprecated)* Legacy environment key - use `FLASK_REMOTE_LOGGING_ENVIRONMENT` instead | `production` |
| `AWS_APP_NAME` | Name of the application sending logs | `app.name` |
| `AWS_SERVICE_NAME` | Name of the service sending logs | `app.name` |
| `FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE` | Enable/disable automatic request/response middleware | `True` |

### Azure Monitor Logs Configuration

| Configuration Key | Description | Default |
|-------------------|-------------|---------|
| `AZURE_WORKSPACE_ID` | Azure Log Analytics workspace ID | Required |
| `AZURE_WORKSPACE_KEY` | Azure Log Analytics workspace key | Required |
| `AZURE_LOG_TYPE` | Custom log type name in Azure Monitor | `FlaskAppLogs` |
| `AZURE_LOG_LEVEL` | Minimum log level | `WARNING` |
| `FLASK_REMOTE_LOGGING_ENVIRONMENT` | **Unified environment key** - Environment where logs should be sent | `production` |
| `AZURE_ENVIRONMENT` | *(Deprecated)* Legacy environment key - use `FLASK_REMOTE_LOGGING_ENVIRONMENT` instead | `production` |
| `AZURE_TIMEOUT` | HTTP request timeout in seconds | `30` |
| `FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE` | Enable/disable automatic request/response middleware | `True` |

### IBM Cloud Logs Configuration

| Configuration Key | Description | Default |
|-------------------|-------------|---------|
| `IBM_INGESTION_KEY` | IBM Cloud Logs ingestion key | Required |
| `IBM_HOSTNAME` | Hostname for log entries | System hostname |
| `IBM_APP_NAME` | Application name for log entries | `flask-app` |
| `IBM_ENV` | Environment name for log entries | `development` |
| `IBM_IP` | IP address for log entries (optional) | `None` |
| `IBM_MAC` | MAC address for log entries (optional) | `None` |
| `IBM_LOG_LEVEL` | Minimum log level | `INFO` |
| `FLASK_REMOTE_LOGGING_ENVIRONMENT` | **Unified environment key** - Environment where logs should be sent | `production` |
| `IBM_ENVIRONMENT` | *(Deprecated)* Legacy environment key - use `FLASK_REMOTE_LOGGING_ENVIRONMENT` instead | `development` |
| `IBM_URL` | IBM Cloud Logs ingestion endpoint | `https://logs.logdna.com/logs/ingest` |
| `IBM_TIMEOUT` | HTTP request timeout in seconds | `30` |
| `IBM_INDEX_META` | Whether metadata should be indexed/searchable | `False` |
| `IBM_TAGS` | Comma-separated list of tags for grouping hosts | `''` |
| `FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE` | Enable/disable automatic request/response middleware | `True` |

### Oracle Cloud Infrastructure Logging Configuration

| Configuration Key | Description | Default |
|-------------------|-------------|---------|
| `OCI_CONFIG_FILE` | Path to OCI config file | `~/.oci/config` |
| `OCI_CONFIG_PROFILE` | OCI config profile name | `DEFAULT` |
| `OCI_LOG_GROUP_ID` | OCI log group OCID (optional) | `None` |
| `OCI_LOG_ID` | OCI log OCID | Required |
| `OCI_COMPARTMENT_ID` | OCI compartment OCID (optional) | `None` |
| `OCI_SOURCE` | Source identifier for log entries | `flask-app` |
| `OCI_LOG_LEVEL` | Minimum log level | `INFO` |
| `FLASK_REMOTE_LOGGING_ENVIRONMENT` | **Unified environment key** - Environment where logs should be sent | `production` |
| `OCI_ENVIRONMENT` | *(Deprecated)* Legacy environment key - use `FLASK_REMOTE_LOGGING_ENVIRONMENT` instead | `development` |
| `FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE` | Enable/disable automatic request/response middleware | `True` |


## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

### Quick Development Setup

```bash
# Clone repository
git clone https://github.com/MarcFord/flask-remote-logging.git
cd flask-remote-logging

# Install dependencies
make install-dev
make install-tools

# Run tests
make test

# Run code quality checks
make lint
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Support

- 📖 **Documentation:** [GitHub Wiki](https://github.com/MarcFord/flask-remote-logging/wiki)
- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/MarcFord/flask-remote-logging/issues)
- 💡 **Feature Requests:** [GitHub Issues](https://github.com/MarcFord/flask-remote-logging/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/MarcFord/flask-remote-logging/discussions)

---

### Badge Information

- **CI Badge**: Shows the status of the latest GitHub Actions workflow run
- **Codecov Badge**: Shows test coverage percentage (updates after coverage upload to codecov.io)
- **Python Badge**: Indicates supported Python versions (3.9+)
- **License Badge**: Shows the project license (MIT)

**After first PyPI release, these badges will also appear:**
```markdown
[![PyPI version](https://badge.fury.io/py/flask-remote-logging.svg)](https://badge.fury.io/py/flask-remote-logging)
[![PyPI downloads](https://img.shields.io/pypi/dm/flask-remote-logging.svg)](https://pypi.org/project/flask-remote-logging/)
```
