# flask-network-logging

[![CI](https://github.com/MarcFord/flask-network-logging/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/MarcFord/flask-network-logging/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/MarcFord/flask-network-logging/branch/main/graph/badge.svg)](https://codecov.io/gh/MarcFord/flask-network-logging)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/MarcFord/flask-network-logging/blob/main/LICENSE)

A Flask extension for sending application logs to remote logging services including Graylog via GELF (Graylog Extended Log Format), Google Cloud Logging, and AWS CloudWatch Logs.

> **📊 Badge Status**: The CI badge shows the latest build status. The codecov badge will update once coverage reports are uploaded to codecov.io. PyPI badges will appear after the first release.

## Features

- 🚀 Easy Flask integration with multiple logging backends
- 📝 Automatic request context logging
- 🔧 Configurable log levels and filtering
- 🌍 Environment-based configuration
- 🏷️ Custom field support
- 🔒 Production-ready with comprehensive testing
- 🐍 Python 3.9+ support
- 📡 Support for Graylog via GELF
- ☁️ Support for Google Cloud Logging
- 🚀 Support for AWS CloudWatch Logs

## Installation

```bash
pip install flask-network-logging
```

## Quick Start

### Graylog Integration

```python
from flask import Flask
from flask_network_logging import Graylog

app = Flask(__name__)

# Configure Graylog
app.config.update({
    'GRAYLOG_HOST': 'your-graylog-server.com',
    'GRAYLOG_PORT': 12201,
    'GRAYLOG_LEVEL': 'INFO',
    'GRAYLOG_ENVIRONMENT': 'production'
})

# Initialize extension
graylog = Graylog(app)
graylog._setup_logging()

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
from flask_network_logging import GCPLog

app = Flask(__name__)

# Configure Google Cloud Logging
app.config.update({
    'GCP_PROJECT_ID': 'your-gcp-project-id',
    'GCP_LOG_NAME': 'flask-app',
    'GCP_LOG_LEVEL': 'INFO',
    'GCP_ENVIRONMENT': 'production'
})

# Initialize extension
gcp_log = GCPLog(app)
gcp_log._setup_logging()

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
from flask_network_logging import AWSLog

app = Flask(__name__)

# Configure AWS CloudWatch Logs
app.config.update({
    'AWS_REGION': 'us-east-1',
    'AWS_LOG_GROUP': '/flask-app/logs',
    'AWS_LOG_STREAM': 'app-stream',
    'AWS_LOG_LEVEL': 'INFO',
    'AWS_ENVIRONMENT': 'production'
})

# Initialize extension
aws_log = AWSLog(app)
aws_log._setup_logging()

@app.route('/')
def hello():
    app.logger.info("Hello world endpoint accessed")
    return "Hello, World!"

if __name__ == '__main__':
    app.run()
```

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

## Configuration

### Graylog Configuration

| Configuration Key | Description | Default |
|-------------------|-------------|---------|
| `GRAYLOG_HOST` | Graylog server hostname | `localhost` |
| `GRAYLOG_PORT` | Graylog GELF UDP port | `12201` |
| `GRAYLOG_LEVEL` | Minimum log level | `WARNING` |
| `GRAYLOG_ENVIRONMENT` | Environment where logs should be sent to graylog | `development` |
| `GRAYLOG_EXTRA_FIELDS` | True to allow extra fields, False if not | True |
| `GRAYLOG_APP_NAME` | Name of the application sending logs | `app.name` |
| `GRAYLOG_SERVICE_NAME` | Name of the service sending logs. Useful if you have an application that is made up of multiple services | `app.name` |

### Google Cloud Logging Configuration

| Configuration Key | Description | Default |
|-------------------|-------------|---------|
| `GCP_PROJECT_ID` | Google Cloud Project ID | Required |
| `GCP_CREDENTIALS_PATH` | Path to service account JSON file (optional if using default credentials) | `None` |
| `GCP_LOG_NAME` | Name of the log in Cloud Logging | `flask-app` |
| `GCP_LOG_LEVEL` | Minimum log level | `WARNING` |
| `GCP_ENVIRONMENT` | Environment where logs should be sent to GCP | `production` |
| `GCP_APP_NAME` | Name of the application sending logs | `app.name` |
| `GCP_SERVICE_NAME` | Name of the service sending logs | `app.name` |

### AWS CloudWatch Logs Configuration

| Configuration Key | Description | Default |
|-------------------|-------------|---------|
| `AWS_REGION` | AWS region for CloudWatch Logs | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key (optional if using IAM roles/profiles) | `None` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key (optional if using IAM roles/profiles) | `None` |
| `AWS_LOG_GROUP` | CloudWatch log group name | `/flask-app/logs` |
| `AWS_LOG_STREAM` | CloudWatch log stream name | `app-stream` |
| `AWS_LOG_LEVEL` | Minimum log level | `WARNING` |
| `AWS_ENVIRONMENT` | Environment where logs should be sent to AWS | `production` |
| `AWS_APP_NAME` | Name of the application sending logs | `app.name` |
| `AWS_SERVICE_NAME` | Name of the service sending logs | `app.name` |


## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

### Quick Development Setup

```bash
# Clone repository
git clone https://github.com/MarcFord/flask-network-logging.git
cd flask-network-logging

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

- 📖 **Documentation:** [GitHub Wiki](https://github.com/MarcFord/flask-network-logging/wiki)
- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/MarcFord/flask-network-logging/issues)
- 💡 **Feature Requests:** [GitHub Issues](https://github.com/MarcFord/flask-network-logging/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/MarcFord/flask-network-logging/discussions)

---

### Badge Information

- **CI Badge**: Shows the status of the latest GitHub Actions workflow run
- **Codecov Badge**: Shows test coverage percentage (updates after coverage upload to codecov.io)
- **Python Badge**: Indicates supported Python versions (3.9+)
- **License Badge**: Shows the project license (MIT)

**After first PyPI release, these badges will also appear:**
```markdown
[![PyPI version](https://badge.fury.io/py/flask-network-logging.svg)](https://badge.fury.io/py/flask-network-logging)
[![PyPI downloads](https://img.shields.io/pypi/dm/flask-network-logging.svg)](https://pypi.org/project/flask-network-logging/)
```
