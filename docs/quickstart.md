# Quick Start Guide

Get up and running with Flask Network Logging in minutes.

## Installation

Choose the installation method that matches your logging backend needs:

### Basic Installation

```bash
pip install flask-remote-logging
```

### Backend-Specific Installation

Install only the dependencies you need:

```bash
# For Graylog
pip install flask-remote-logging[graylog]

# For AWS CloudWatch
pip install flask-remote-logging[aws]

# For Google Cloud Logging
pip install flask-network_logging[gcp]

# For Azure Monitor
pip install flask-remote-logging[azure]

# For IBM Cloud Logs
pip install flask-remote-logging[ibm]

# For Oracle Cloud Infrastructure
pip install flask-remote-logging[oci]

# For multiple backends
pip install flask-remote-logging[graylog,aws,gcp]

# For all backends
pip install flask-remote-logging[all]
```

## Your First Logging Setup

### 1. Basic Graylog Example

```python
from flask import Flask
from flask_remote_logging import GraylogExtension

app = Flask(__name__)

# Configure Graylog
app.config.update({
    'GRAYLOG_HOST': 'localhost',
    'GRAYLOG_PORT': 12201,
    'GRAYLOG_LEVEL': 'INFO',
})

# Initialize extension (logging setup is automatic)
graylog = GraylogExtension(app)

@app.route('/')
def hello():
    app.logger.info("Hello world endpoint accessed")
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
```

### 2. AWS CloudWatch Example

```python
from flask import Flask
from flask_remote_logging import AWSLogExtension

app = Flask(__name__)

# Configure AWS CloudWatch
app.config.update({
    'AWS_REGION': 'us-east-1',
    'AWS_LOG_GROUP': '/flask-app/logs',
    'AWS_LOG_STREAM': 'app-stream',
})

# Initialize extension
aws_log = AWSLogExtension(app)

@app.route('/')
def hello():
    app.logger.info("Hello from AWS CloudWatch!")
    return "Hello, AWS!"
```

### 3. Google Cloud Logging Example

```python
from flask import Flask
from flask_remote_logging import GCPLogExtension

app = Flask(__name__)

# Configure Google Cloud Logging
app.config.update({
    'GCP_PROJECT_ID': 'your-project-id',
    'GCP_LOG_NAME': 'flask-app',
})

# Initialize extension
gcp_log = GCPLogExtension(app)

@app.route('/')
def hello():
    app.logger.info("Hello from Google Cloud!")
    return "Hello, GCP!"
```

## Key Features Demonstrated

### Automatic Setup

No manual setup required - logging is configured automatically:

```python
# Old way (no longer needed):
# extension = GraylogExtension(app)
# extension._setup_logging()

# New way (automatic):
extension = GraylogExtension(app)  # That's it!
```

### Request/Response Middleware

Automatic request and response logging is enabled by default:

```python
# Logs are automatically generated for:
# - Request start time
# - Request method, path, headers
# - Response status, headers, timing
# - User context (if available)
```

### Environment-Based Configuration

Configure different settings for different environments:

```python
app.config.update({
    'GRAYLOG_HOST': 'localhost',  # Development
    'GRAYLOG_ENVIRONMENT': 'development',
})

# In production, use environment variables:
# GRAYLOG_HOST=prod-graylog.company.com
# GRAYLOG_ENVIRONMENT=production
```

## Configuration Options

### Common Settings

All extensions support these common configuration patterns:

```python
app.config.update({
    # Backend-specific connection settings
    'GRAYLOG_HOST': 'your-server.com',
    
    # Log level control
    'GRAYLOG_LOG_LEVEL': 'INFO',
    
    # Environment filtering
    'GRAYLOG_ENVIRONMENT': 'production',
    
    # Middleware control
    'FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE': True,
})
```

### Disable Middleware

If you want to handle logging manually:

```python
# Disable via parameter
graylog = GraylogExtension(app, enable_middleware=False)

# Or via configuration
app.config['FLASK_REMOTE_LOGGING_ENABLE_MIDDLEWARE'] = False
graylog = GraylogExtension(app)
```

## Testing Your Setup

### 1. Run the Application

```bash
python app.py
```

### 2. Generate Some Logs

```bash
# Visit your application
curl http://localhost:5000/

# Check for logs in your logging backend
```

### 3. Verify Log Content

Look for logs containing:
- Request information (method, path, IP)
- Response information (status code, timing)
- Your custom log messages
- Context information (user, session, etc.)

## What's Next?

- **[Configuration Guide](configuration.md)** - Complete configuration reference
- **[User Guide](user_guide/index.md)** - Detailed usage patterns
- **[Cloud Provider Guides](providers/index.md)** - Backend-specific setup
- **[Examples](examples/index.md)** - More complex examples

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Make sure you installed the right backend dependencies
pip install flask-remote-logging[graylog]
```

**Connection Issues**
```python
# Check your configuration
print(app.config)
# Verify network connectivity to your logging backend
```

**No Logs Appearing**
```python
# Check the environment setting
app.config['GRAYLOG_ENVIRONMENT'] = 'development'  # Match your Flask env
```

Need more help? Check the [full documentation](user_guide/index.md) or [open an issue](https://github.com/MarcFord/flask-remote-logging/issues).
