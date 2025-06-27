# Advanced Configuration

## Custom Log Formatting

You can customize how logs are formatted before sending to remote services:

```python
import logging
from flask_remote_logging import RemoteLogging

def custom_formatter(record):
    """Custom log formatter function."""
    return {
        'message': record.getMessage(),
        'level': record.levelname,
        'timestamp': record.created,
        'custom_field': 'custom_value'
    }

app.config['NETWORK_LOGGING_FORMATTER'] = custom_formatter
```

## Filtering Logs

Control which logs get sent to remote services:

```python
def log_filter(record):
    """Only send ERROR and CRITICAL logs."""
    return record.levelno >= logging.ERROR

app.config['NETWORK_LOGGING_FILTER'] = log_filter
```

## Performance Tuning

- Use buffering for high-volume applications
- Configure appropriate timeouts
- Consider async handlers for non-blocking operation
