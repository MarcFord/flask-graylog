# Graylog

Graylog is an open-source log management platform. This backend uses GELF (Graylog Extended Log Format) to send logs.

## Installation

```bash
pip install flask-remote-logging[graylog]
```

## Configuration

```python
from flask import Flask
from flask_remote_logging import RemoteLogging

app = Flask(__name__)

# Basic Graylog configuration
app.config['GRAYLOG_HOST'] = 'your-graylog-server.com'
app.config['GRAYLOG_PORT'] = 12201
app.config['GRAYLOG_FACILITY'] = 'flask-app'

# Optional SSL configuration
app.config['GRAYLOG_USE_TLS'] = True
app.config['GRAYLOG_CERT_PATH'] = '/path/to/cert'

network_logging = RemoteLogging()
network_logging.init_app(app)
```

## Available Options

- `GRAYLOG_HOST`: Graylog server hostname
- `GRAYLOG_PORT`: GELF UDP port (default: 12201)
- `GRAYLOG_FACILITY`: Application identifier
- `GRAYLOG_USE_TLS`: Enable TLS (default: False)
- `GRAYLOG_CERT_PATH`: Path to SSL certificate
