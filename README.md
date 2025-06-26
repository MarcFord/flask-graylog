# flask-graylog

[![CI](https://github.com/MarcFord/flask-graylog/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/MarcFord/flask-graylog/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/MarcFord/flask-graylog/branch/main/graph/badge.svg)](https://codecov.io/gh/MarcFord/flask-graylog)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/MarcFord/flask-graylog/blob/main/LICENSE)

A Flask extension for sending application logs to Graylog via GELF (Graylog Extended Log Format).

> **📊 Badge Status**: The CI badge shows the latest build status. The codecov badge will update once coverage reports are uploaded to codecov.io. PyPI badges will appear after the first release.

## Features

- 🚀 Easy Flask integration
- 📝 Automatic request context logging
- 🔧 Configurable log levels and filtering
- 🌍 Environment-based configuration
- 🏷️ Custom field support
- 🔒 Production-ready with comprehensive testing
- 🐍 Python 3.9+ support

## Installation

```bash
pip install flask-graylog
```

## Quick Start

```python
from flask import Flask
from flask_graylog import Graylog

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

| Configuration Key | Description | Default |
|-------------------|-------------|---------|
| `GRAYLOG_HOST` | Graylog server hostname | `localhost` |
| `GRAYLOG_PORT` | Graylog GELF UDP port | `12201` |
| `GRAYLOG_LEVEL` | Minimum log level | `WARNING` |
| `GRAYLOG_ENVIRONMENT` | Environment where logs should be sent to graylog | `development` |
| `GRAYLOG_EXTRA_FIELDS` | True to allow extra fields, False if not | True |
| `GRAYLOG_APP_NAME` | Name of the application sending logs | `app.name` |
| `GRAYLOG_SERVICE_NAME` | Name of the service sending logs. Useful if you have an application that is made up of multiple services | `app.name` |


## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

### Quick Development Setup

```bash
# Clone repository
git clone https://github.com/MarcFord/flask-graylog.git
cd flask-graylog

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

- 📖 **Documentation:** [GitHub Wiki](https://github.com/MarcFord/flask-graylog/wiki)
- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/MarcFord/flask-graylog/issues)
- 💡 **Feature Requests:** [GitHub Issues](https://github.com/MarcFord/flask-graylog/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/MarcFord/flask-graylog/discussions)

---

### Badge Information

- **CI Badge**: Shows the status of the latest GitHub Actions workflow run
- **Codecov Badge**: Shows test coverage percentage (updates after coverage upload to codecov.io)
- **Python Badge**: Indicates supported Python versions (3.9+)
- **License Badge**: Shows the project license (MIT)

**After first PyPI release, these badges will also appear:**
```markdown
[![PyPI version](https://badge.fury.io/py/flask-graylog.svg)](https://badge.fury.io/py/flask-graylog)
[![PyPI downloads](https://img.shields.io/pypi/dm/flask-graylog.svg)](https://pypi.org/project/flask-graylog/)
```
