# Configuration

This section covers configuration options for Flask Network Logging.

## Basic Configuration

```python
from flask import Flask
from flask_remote_logging import RemoteLogging

app = Flask(__name__)
app.config['NETWORK_LOGGING_ENABLED'] = True
app.config['NETWORK_LOGGING_BACKENDS'] = ['graylog']

# Graylog configuration
app.config['GRAYLOG_HOST'] = 'localhost'
app.config['GRAYLOG_PORT'] = 12201
app.config['GRAYLOG_FACILITY'] = 'flask-app'

network_logging = RemoteLogging()
network_logging.init_app(app)
```

## Advanced Configuration

See the [User Guide](user_guide/index.md) for detailed configuration options.
