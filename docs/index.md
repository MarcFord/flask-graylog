# Flask Network Logging Documentation

[![CI](https://github.com/MarcFord/flask-remote-logging/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/MarcFord/flask-remote-logging/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/MarcFord/flask-remote-logging/branch/main/graph/badge.svg)](https://codecov.io/gh/MarcFord/flask-remote-logging)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/MarcFord/flask-remote-logging/blob/main/LICENSE)

A comprehensive Flask extension for sending application logs to remote logging services including Graylog, Google Cloud Logging, AWS CloudWatch Logs, Azure Monitor Logs, IBM Cloud Logs, and Oracle Cloud Infrastructure Logging.

## Quick Navigation

```{toctree}
:maxdepth: 2
:caption: Getting Started

quickstart
installation
configuration
```

```{toctree}
:maxdepth: 2
:caption: User Guide

user_guide/index
user_guide/backends
user_guide/middleware
user_guide/factory_pattern
user_guide/advanced_config
```

```{toctree}
:maxdepth: 2
:caption: Cloud Provider Guides

providers/graylog
providers/aws
providers/azure
providers/gcp
providers/ibm
providers/oci
```

```{toctree}
:maxdepth: 2
:caption: Examples

examples/index
examples/single_backend
examples/multi_backend
examples/production
```

```{toctree}
:maxdepth: 2
:caption: API Reference

api/index
api/extensions
api/filters
api/middleware
api/handlers
```

```{toctree}
:maxdepth: 1
:caption: Developer Resources

contributing
changelog
license
```

## Features Overview

- 🚀 **Easy Flask Integration**: Simple setup with multiple logging backends
- 📝 **Automatic Request Context**: Built-in request/response middleware logging
- 🔧 **Configurable**: Flexible log levels, filtering, and custom fields
- 🌍 **Environment-Based**: Production/development environment configuration
- 🏷️ **Custom Field Support**: Add metadata to your log messages
- 🔒 **Production-Ready**: Comprehensive testing and error handling
- 🐍 **Python 3.9+ Support**: Modern Python compatibility
- 📡 **Multiple Backends**: Support for 6+ logging services

## Supported Backends

| Backend | Status | Features |
|---------|--------|----------|
| **Graylog** | ✅ Full Support | GELF protocol, structured logging |
| **AWS CloudWatch** | ✅ Full Support | Log groups/streams, IAM integration |
| **Google Cloud Logging** | ✅ Full Support | Cloud Logging API, service account auth |
| **Azure Monitor** | ✅ Full Support | Log Analytics workspace integration |
| **IBM Cloud Logs** | ✅ Full Support | LogDNA ingestion API |
| **Oracle Cloud (OCI)** | ✅ Full Support | OCI Logging service integration |

## Getting Started

### Installation

```bash
# Install with specific backend support
pip install flask-remote-logging[graylog,aws,gcp]

# Or install all backends
pip install flask-remote-logging[all]
```

### Basic Usage

```python
from flask import Flask
from flask_remote_logging import GraylogExtension

app = Flask(__name__)
app.config.update({
    'GRAYLOG_HOST': 'your-graylog-server.com',
    'GRAYLOG_PORT': 12201,
})

# Automatic setup - no manual configuration needed
graylog = GraylogExtension(app)

@app.route('/')
def hello():
    app.logger.info("Hello world endpoint accessed")
    return "Hello, World!"
```

## What's New

- **Automatic Setup**: No more manual `_setup_logging()` calls
- **Middleware Control**: Enable/disable request logging per extension
- **Factory Pattern**: Full Flask application factory support
- **Type Safety**: Comprehensive type annotations
- **Better Error Handling**: Graceful fallbacks and error reporting

## Quick Links

- **[Installation Guide](installation.md)** - Get up and running quickly
- **[Configuration Reference](configuration.md)** - Complete config options
- **[Cloud Provider Guides](providers/index.md)** - Backend-specific setup
- **[Examples](examples/index.md)** - Real-world usage examples
- **[API Reference](api/index.md)** - Complete API documentation

## Community & Support

- 📖 **Documentation**: You're reading it!
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/MarcFord/flask-remote-logging/issues)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/MarcFord/flask-remote-logging/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/MarcFord/flask-remote-logging/discussions)
- 🤝 **Contributing**: [Contributing Guide](contributing.md)
