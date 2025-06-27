# Middleware

Flask Network Logging includes middleware functionality that captures HTTP request/response information automatically.

## Configuration

The middleware can be controlled through configuration:

```python
# Enable/disable middleware globally
app.config['NETWORK_LOGGING_ENABLE_MIDDLEWARE'] = True

# Control what gets logged
app.config['NETWORK_LOGGING_LOG_REQUEST_HEADERS'] = True
app.config['NETWORK_LOGGING_LOG_RESPONSE_HEADERS'] = False
```

## Per-Backend Control

Each backend can have middleware enabled or disabled independently:

```python
# When initializing extensions
aws_logging = AWSLogExtension(enable_middleware=False)
```
