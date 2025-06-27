# Extensions API

Complete API reference for logging extension classes.

## Base Extension

```{eval-rst}
.. autoclass:: flask_remote_logging.base_extension.BaseLoggingExtension
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

## Graylog Extension

```{eval-rst}
.. autoclass:: flask_remote_logging.GraylogExtension
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

### Example Usage

```python
from flask import Flask
from flask_remote_logging import GraylogExtension

app = Flask(__name__)
app.config.update({
    'GRAYLOG_HOST': 'localhost',
    'GRAYLOG_PORT': 12201,
    'GRAYLOG_LEVEL': 'INFO',
})

# Basic usage
graylog = GraylogExtension(app)

# With custom user function
def get_current_user():
    return {'id': 123, 'name': 'John Doe'}

graylog = GraylogExtension(
    app=app,
    get_current_user=get_current_user,
    log_level=logging.DEBUG,
    enable_middleware=True,
)
```

## AWS CloudWatch Extension

```{eval-rst}
.. autoclass:: flask_remote_logging.AWSLogExtension
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

### Example Usage

```python
from flask import Flask
from flask_remote_logging import AWSLogExtension

app = Flask(__name__)
app.config.update({
    'AWS_REGION': 'us-east-1',
    'AWS_LOG_GROUP': '/flask-app/logs',
    'AWS_LOG_STREAM': 'app-stream',
})

aws_log = AWSLogExtension(app)
```

## Google Cloud Logging Extension

```{eval-rst}
.. autoclass:: flask_remote_logging.GCPLogExtension
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

### Example Usage

```python
from flask import Flask
from flask_remote_logging import GCPLogExtension

app = Flask(__name__)
app.config.update({
    'GCP_PROJECT_ID': 'my-project',
    'GCP_LOG_NAME': 'flask-app',
})

gcp_log = GCPLogExtension(app)
```

## Azure Monitor Extension

```{eval-rst}
.. autoclass:: flask_remote_logging.AzureLogExtension
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

### Example Usage

```python
from flask import Flask
from flask_remote_logging import AzureLogExtension

app = Flask(__name__)
app.config.update({
    'AZURE_WORKSPACE_ID': 'workspace-id',
    'AZURE_WORKSPACE_KEY': 'workspace-key',
    'AZURE_LOG_TYPE': 'FlaskAppLogs',
})

azure_log = AzureLogExtension(app)
```

## IBM Cloud Logs Extension

```{eval-rst}
.. autoclass:: flask_remote_logging.IBMLogExtension
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

### Example Usage

```python
from flask import Flask
from flask_remote_logging import IBMLogExtension

app = Flask(__name__)
app.config.update({
    'IBM_INGESTION_KEY': 'ingestion-key',
    'IBM_HOSTNAME': 'my-app',
    'IBM_APP_NAME': 'flask-app',
})

ibm_log = IBMLogExtension(app)
```

## Oracle Cloud Infrastructure Extension

```{eval-rst}
.. autoclass:: flask_remote_logging.OCILogExtension
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
```

### Example Usage

```python
from flask import Flask
from flask_remote_logging import OCILogExtension

app = Flask(__name__)
app.config.update({
    'OCI_LOG_ID': 'ocid1.log.oc1...',
    'OCI_SOURCE': 'flask-app',
})

oci_log = OCILogExtension(app)
```

## Common Parameters

All extensions support these common initialization parameters:

### app: Flask
The Flask application instance to integrate with.

### get_current_user: Optional[Callable]
Function that returns current user information. Should return a dict with user details.

```python
def get_current_user():
    from flask_login import current_user
    if current_user.is_authenticated:
        return {
            'id': current_user.id,
            'email': current_user.email,
            'username': current_user.username,
        }
    return None
```

### log_level: int
Minimum log level for the extension. Can be a logging module constant or string.

```python
import logging

# Using constants
graylog = GraylogExtension(app, log_level=logging.DEBUG)

# Using strings (converted internally)
graylog = GraylogExtension(app, log_level='DEBUG')
```

### additional_logs: Optional[List[str]]
List of additional logger names to configure with the same handler.

```python
graylog = GraylogExtension(
    app,
    additional_logs=['sqlalchemy.engine', 'urllib3.connectionpool']
)
```

### context_filter: Optional[logging.Filter]
Custom logging filter to add context to log records.

```python
class CustomFilter(logging.Filter):
    def filter(self, record):
        record.custom_field = 'custom_value'
        return True

graylog = GraylogExtension(app, context_filter=CustomFilter())
```

### log_formatter: Optional[logging.Formatter]
Custom log formatter for the handler.

```python
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
graylog = GraylogExtension(app, log_formatter=formatter)
```

### enable_middleware: bool
Whether to enable automatic request/response middleware logging.

```python
# Disable middleware
graylog = GraylogExtension(app, enable_middleware=False)

# Enable middleware (default)
graylog = GraylogExtension(app, enable_middleware=True)
```

## Extension Methods

### init_app(app: Flask) -> None
Initialize the extension with a Flask application. Useful for application factory pattern.

```python
graylog = GraylogExtension()

def create_app():
    app = Flask(__name__)
    graylog.init_app(app)
    return app
```

### _setup_logging() -> None
**Deprecated:** Manual logging setup. This is now called automatically during initialization.

### _get_config_from_app() -> Dict[str, Any]
Get configuration dictionary from the Flask application. Returns all relevant config keys for the extension.

### _should_skip_setup() -> bool
Determine if logging setup should be skipped based on environment configuration.

### _create_log_handler() -> logging.Handler
Create and configure the backend-specific log handler.

### _get_extension_name() -> str
Get the human-readable name of the extension (e.g., "Graylog").

### _get_middleware_config_key() -> str
Get the configuration key for middleware control.

## Error Handling

All extensions include comprehensive error handling:

```python
try:
    graylog = GraylogExtension(app)
except ImportError:
    # Backend dependencies not installed
    app.logger.warning("Graylog support not available")
except ConnectionError:
    # Cannot connect to backend service
    app.logger.error("Cannot connect to Graylog server")
except Exception as e:
    # Other configuration or setup errors
    app.logger.error(f"Logging setup failed: {e}")
```

## Configuration Reference

Each extension uses backend-specific configuration keys. See the [Configuration Guide](../configuration.md) for complete details.
