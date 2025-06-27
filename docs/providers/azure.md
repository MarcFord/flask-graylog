# Azure Monitor Logs

Send logs to Azure Monitor Logs (formerly Log Analytics).

## Installation

```bash
pip install flask-remote-logging[azure]
```

## Configuration

```python
from flask import Flask
from flask_remote_logging import AzureLogExtension

app = Flask(__name__)

# Azure configuration
app.config['AZURE_WORKSPACE_ID'] = 'your-workspace-id'
app.config['AZURE_SHARED_KEY'] = 'your-shared-key'
app.config['AZURE_LOG_TYPE'] = 'FlaskLogs'

azure_logging = AzureLogExtension()
azure_logging.init_app(app)
```

## Getting Credentials

1. Navigate to your Log Analytics workspace in Azure Portal
2. Go to Settings → Agents management
3. Copy the Workspace ID and Primary Key
4. Use these as `AZURE_WORKSPACE_ID` and `AZURE_SHARED_KEY`

## Custom Log Types

Azure allows custom log types. Set `AZURE_LOG_TYPE` to define your log table name. Logs will appear in a table named `{LOG_TYPE}_CL`.
