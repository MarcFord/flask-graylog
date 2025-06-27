# Google Cloud Logging

Send logs to Google Cloud Logging (formerly Stackdriver).

## Installation

```bash
pip install flask-remote-logging[gcp]
```

## Configuration

```python
from flask import Flask
from flask_remote_logging import GCPLogExtension

app = Flask(__name__)

# GCP configuration
app.config['GCP_PROJECT_ID'] = 'your-project-id'
app.config['GCP_LOG_NAME'] = 'flask-app'

# Optional: specify credentials file
app.config['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/service-account.json'

gcp_logging = GCPLogExtension()
gcp_logging.init_app(app)
```

## Authentication

### Service Account

1. Create a service account in Google Cloud Console
2. Download the JSON key file  
3. Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable or config

### Application Default Credentials

If running on Google Cloud Platform (App Engine, Compute Engine, etc.), authentication is handled automatically.

## Required Permissions

The service account needs the `Logs Writer` role or these specific permissions:

- `logging.logEntries.create`
- `logging.logs.write`
