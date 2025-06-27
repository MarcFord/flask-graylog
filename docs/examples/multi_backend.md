# Multi-Backend Examples

## Multiple Cloud Providers

```python
from flask import Flask
from flask_remote_logging import AWSLogExtension, GCPLogExtension, AzureLogExtension

app = Flask(__name__)

# AWS configuration
app.config['AWS_REGION'] = 'us-east-1'
app.config['AWS_LOG_GROUP'] = 'flask-app-logs'
app.config['AWS_LOG_STREAM'] = 'production'

# GCP configuration
app.config['GCP_PROJECT_ID'] = 'my-project'
app.config['GCP_LOG_NAME'] = 'flask-app'

# Azure configuration
app.config['AZURE_WORKSPACE_ID'] = 'workspace-id'
app.config['AZURE_SHARED_KEY'] = 'shared-key'
app.config['AZURE_LOG_TYPE'] = 'FlaskLogs'

# Initialize all backends
aws_logging = AWSLogExtension()
gcp_logging = GCPLogExtension()
azure_logging = AzureLogExtension()

aws_logging.init_app(app)
gcp_logging.init_app(app)
azure_logging.init_app(app)

@app.route('/')
def hello():
    # This log will go to all three services
    app.logger.info('Multi-cloud logging example')
    return 'Logging to AWS, GCP, and Azure!'

if __name__ == '__main__':
    app.run(debug=True)
```

## Selective Backend Configuration

```python
from flask import Flask
from flask_remote_logging import RemoteLogging, AWSLogExtension

app = Flask(__name__)

# Configure both Graylog and AWS
app.config['GRAYLOG_HOST'] = 'localhost'
app.config['GRAYLOG_PORT'] = 12201
app.config['GRAYLOG_FACILITY'] = 'flask-app'

app.config['AWS_REGION'] = 'us-east-1'
app.config['AWS_LOG_GROUP'] = 'flask-app-logs'

# Initialize with middleware control
network_logging = RemoteLogging()  # Default middleware enabled
aws_logging = AWSLogExtension(enable_middleware=False)  # No middleware

network_logging.init_app(app)
aws_logging.init_app(app)
```
