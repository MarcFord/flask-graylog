# Azure Monitor Logs Flask Example

This example demonstrates how to integrate Flask with Azure Monitor Logs (Log Analytics) using the `flask-remote-logging` package.

## Features

- **Azure Monitor Logs Integration**: Send logs directly to Azure Log Analytics workspace
- **Request Context Logging**: Automatic logging of request details with correlation IDs
- **Structured Logging**: JSON-formatted logs with custom fields and metadata
- **Performance Monitoring**: Log request timing and performance metrics
- **Error Handling**: Comprehensive error logging with stack traces
- **Health Checks**: Built-in health check endpoint with Azure metadata

## Prerequisites

1. **Azure Subscription**: You need an active Azure subscription
2. **Log Analytics Workspace**: Create a Log Analytics workspace in the Azure portal
3. **Workspace Credentials**: Get the Workspace ID and Primary Key from the workspace

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create Log Analytics Workspace** (if not exists):
   ```bash
   # Using Azure CLI
   az monitor log-analytics workspace create \
     --resource-group myResourceGroup \
     --workspace-name myWorkspace \
     --location eastus
   ```

3. **Get Workspace Credentials**:
   ```bash
   # Get Workspace ID
   az monitor log-analytics workspace show \
     --resource-group myResourceGroup \
     --workspace-name myWorkspace \
     --query customerId -o tsv
   
   # Get Primary Key
   az monitor log-analytics workspace get-shared-keys \
     --resource-group myResourceGroup \
     --workspace-name myWorkspace \
     --query primarySharedKey -o tsv
   ```

4. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Azure workspace details
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```

## Configuration

The application can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `AZURE_WORKSPACE_ID` | Log Analytics Workspace ID | `your-workspace-id` |
| `AZURE_WORKSPACE_KEY` | Log Analytics Primary Key | `your-workspace-key` |
| `AZURE_LOG_TYPE` | Custom log type name | `FlaskAppLogs` |
| `AZURE_LOG_LEVEL` | Logging level | `INFO` |
| `AZURE_ENVIRONMENT` | Environment name | `development` |
| `AZURE_RESOURCE_ID` | Azure resource identifier (optional) | None |
| `PORT` | Server port | `5000` |

## API Endpoints

- `GET /` - Home page with API information
- `GET /health` - Health check with Azure metadata
- `GET /users` - Mock users API with structured logging
- `GET /logs/test` - Test different log levels
- `GET /logs/user-context` - Test user context logging
- `GET /logs/error` - Test error logging and exception handling
- `GET /logs/azure-metrics` - Test Azure-specific metrics and structured logging
- `GET /logs/performance` - Test performance logging with timing

## Usage Examples

### Test Basic Logging
```bash
curl http://localhost:5000/logs/test
```

### Test User Context (with Azure AD headers)
```bash
curl -H "X-User-ID: alice123" \
     -H "X-Username: alice" \
     -H "X-User-Email: alice@example.com" \
     -H "X-MS-CLIENT-PRINCIPAL-NAME: alice@company.com" \
     -H "X-MS-CLIENT-PRINCIPAL-ID: 12345678-1234-1234-1234-123456789abc" \
     http://localhost:5000/logs/user-context
```

### Test Error Logging
```bash
curl http://localhost:5000/logs/error
```

### Test Performance Metrics
```bash
curl http://localhost:5000/logs/performance
```

## Viewing Logs

You can view the logs in Azure Monitor:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Log Analytics workspace
3. Go to "Logs" section
4. Query your custom logs:
   ```kusto
   FlaskAppLogs_CL
   | where TimeGenerated > ago(1h)
   | order by TimeGenerated desc
   ```

### Useful KQL Queries

**View all logs from the last hour:**
```kusto
FlaskAppLogs_CL
| where TimeGenerated > ago(1h)
| order by TimeGenerated desc
```

**Filter by log level:**
```kusto
FlaskAppLogs_CL
| where level_s == "ERROR"
| order by TimeGenerated desc
```

**Request performance analysis:**
```kusto
FlaskAppLogs_CL
| where message_s contains "Request completed"
| extend duration = todouble(duration_ms_d)
| summarize avg(duration), max(duration), min(duration) by bin(TimeGenerated, 5m)
```

**Error rate monitoring:**
```kusto
FlaskAppLogs_CL
| where message_s contains "Request completed"
| summarize 
    TotalRequests = count(),
    ErrorRequests = countif(status_code_d >= 400)
| extend ErrorRate = (ErrorRequests * 100.0) / TotalRequests
```

## Development

For local development, the application will:
- Log to both Azure Monitor Logs and console (stdout)
- Include detailed request context and timing
- Show helpful error messages for configuration issues

## Troubleshooting

### Invalid Workspace ID or Key
```
requests.exceptions.HTTPError: 403 Client Error: Forbidden
```
**Solution**: Verify your `AZURE_WORKSPACE_ID` and `AZURE_WORKSPACE_KEY` are correct.

### Network Issues
```
requests.exceptions.ConnectionError
```
**Solution**: Check your internet connection and Azure service status.

### Log Type Issues
Custom log types appear with `_CL` suffix in Log Analytics. If you set `AZURE_LOG_TYPE=FlaskAppLogs`, your logs will appear in the `FlaskAppLogs_CL` table.

## Production Deployment

For production deployment on Azure:

1. **App Service**: Use App Settings to configure environment variables
2. **Container Instances**: Set environment variables in the container definition
3. **Virtual Machines**: Configure environment variables or use Azure Key Vault
4. **AKS**: Use ConfigMaps and Secrets for configuration

### Azure Key Vault Integration
Store sensitive configuration in Azure Key Vault:

```bash
# Store workspace key in Key Vault
az keyvault secret set \
  --vault-name myKeyVault \
  --name "azure-workspace-key" \
  --value "your-workspace-key"
```

## Additional Resources

- [Azure Monitor Logs Documentation](https://docs.microsoft.com/en-us/azure/azure-monitor/logs/)
- [Log Analytics Data Collector API](https://docs.microsoft.com/en-us/azure/azure-monitor/logs/data-collector-api)
- [flask-remote-logging Documentation](../../README.md)
- [KQL Query Language Reference](https://docs.microsoft.com/en-us/azure/data-explorer/kusto/query/)
