# Factory Pattern

Flask Network Logging works seamlessly with Flask application factories.

## Basic Factory Pattern

```python
from flask import Flask
from flask_remote_logging import RemoteLogging

# Create extension instance outside factory
network_logging = RemoteLogging()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extension
    network_logging.init_app(app)
    
    return app
```

## Multiple Backends

```python
from flask_remote_logging import AWSLogExtension, GCPLogExtension

aws_extension = AWSLogExtension()
gcp_extension = GCPLogExtension()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize multiple backends
    aws_extension.init_app(app)
    gcp_extension.init_app(app)
    
    return app
```
