# Factory Pattern

Flask Network Logging works seamlessly with Flask application factories.

## Basic Factory Pattern

```python
from flask import Flask
from flask_network_logging import NetworkLogging

# Create extension instance outside factory
network_logging = NetworkLogging()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extension
    network_logging.init_app(app)
    
    return app
```

## Multiple Backends

```python
from flask_network_logging import AWSExtension, GCPExtension

aws_extension = AWSExtension()
gcp_extension = GCPExtension()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize multiple backends
    aws_extension.init_app(app)
    gcp_extension.init_app(app)
    
    return app
```
