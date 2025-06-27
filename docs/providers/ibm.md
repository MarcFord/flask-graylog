# IBM Cloud Logs

Send logs to IBM Cloud Logs service.

## Installation

```bash
pip install flask-remote-logging[ibm]
```

## Configuration

```python
from flask import Flask
from flask_remote_logging import IBMLogExtension

app = Flask(__name__)

# IBM Cloud configuration
app.config['IBM_INGESTION_URL'] = 'https://your-instance.logdna.com/logs/ingest'
app.config['IBM_INGESTION_KEY'] = 'your-ingestion-key'
app.config['IBM_HOSTNAME'] = 'flask-app'

ibm_logging = IBMLogExtension()
ibm_logging.init_app(app)
```

## Getting Credentials

1. Go to your IBM Cloud Logs instance
2. Navigate to Settings → API Keys
3. Generate or copy an existing ingestion key
4. Get the ingestion URL from the same page

## Configuration Options

- `IBM_INGESTION_URL`: The logs ingestion endpoint
- `IBM_INGESTION_KEY`: Authentication key for the service
- `IBM_HOSTNAME`: Identifier for your application
- `IBM_TAGS`: Optional comma-separated tags for log categorization
