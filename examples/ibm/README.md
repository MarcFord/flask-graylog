# IBM Cloud Logging Flask Example

This example demonstrates how to integrate Flask with IBM Cloud Logging (LogDNA) using the `flask-remote-logging` package.

## Features

- **IBM Cloud Logging Integration**: Send logs directly to IBM Cloud Logging (LogDNA)
- **Request Context Logging**: Automatic logging of request details with correlation IDs
- **Structured Logging**: JSON-formatted logs with custom fields and metadata
- **Performance Monitoring**: Log request timing and performance metrics
- **Error Handling**: Comprehensive error logging with stack traces
- **Health Checks**: Built-in health check endpoint with IBM metadata

## Prerequisites

1. **IBM Cloud Account**: You need an active IBM Cloud account
2. **IBM Cloud Logging Instance**: Create a LogDNA instance in IBM Cloud
3. **Ingestion Key**: Get the ingestion key from your LogDNA instance

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create LogDNA Instance** (if not exists):
   ```bash
   # Using IBM Cloud CLI
   ibmcloud resource service-instance-create my-logdna logdna 30-day us-south
   ```

3. **Get Ingestion Key**:
   ```bash
   # Get service credentials
   ibmcloud resource service-key-create my-logdna-key Manager --instance-name my-logdna
   ibmcloud resource service-key my-logdna-key
   ```

4. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your IBM Cloud Logging details
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```

## Configuration

The application can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `IBM_INGESTION_KEY` | LogDNA ingestion key | `your-ingestion-key` |
| `IBM_LOG_ENDPOINT` | LogDNA endpoint URL | `logs.us-south.logging.cloud.ibm.com` |
| `IBM_LOG_LEVEL` | Logging level | `INFO` |
| `IBM_ENVIRONMENT` | Environment name | `development` |
| `IBM_APP_NAME` | Application name | `flask-ibm-example` |
| `IBM_HOSTNAME` | Hostname identifier | `localhost` |
| `PORT` | Server port | `5000` |

### Regional Endpoints

Choose the appropriate endpoint based on your LogDNA instance region:

- **US South**: `logs.us-south.logging.cloud.ibm.com`
- **US East**: `logs.us-east.logging.cloud.ibm.com`
- **EU Germany**: `logs.eu-de.logging.cloud.ibm.com`
- **EU United Kingdom**: `logs.eu-gb.logging.cloud.ibm.com`
- **Asia Pacific Tokyo**: `logs.jp-tok.logging.cloud.ibm.com`
- **Asia Pacific Sydney**: `logs.au-syd.logging.cloud.ibm.com`

## API Endpoints

- `GET /` - Home page with API information
- `GET /health` - Health check with IBM metadata
- `GET /users` - Mock users API with structured logging
- `GET /logs/test` - Test different log levels
- `GET /logs/user-context` - Test user context logging
- `GET /logs/error` - Test error logging and exception handling
- `GET /logs/ibm-metrics` - Test IBM-specific metrics and structured logging
- `GET /logs/performance` - Test performance logging with timing

## Usage Examples

### Test Basic Logging
```bash
curl http://localhost:5000/logs/test
```

### Test User Context (with IBM IAM headers)
```bash
curl -H "X-User-ID: alice123" \
     -H "X-Username: alice" \
     -H "X-User-Email: alice@example.com" \
     -H "X-IBM-User-ID: alice@company.com" \
     -H "X-IBM-Subject: IBMid-123456789" \
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

You can view the logs in IBM Cloud Logging:

1. Go to [IBM Cloud Console](https://cloud.ibm.com)
2. Navigate to "Observability" → "Logging"
3. Open your LogDNA instance
4. Use the search and filter capabilities to find your logs

### LogDNA Search Examples

**View all logs from your app:**
```
app:flask-ibm-example
```

**Filter by log level:**
```
level:ERROR
```

**Search for specific messages:**
```
"Request completed" AND status_code:>=400
```

**Time-based queries:**
```
"Request started" AND timestamp:>now-1h
```

**Performance analysis:**
```
"duration_ms" AND endpoint:index
```

## Development

For local development, the application will:
- Log to both IBM Cloud Logging and console (stdout)
- Include detailed request context and timing
- Show helpful error messages for configuration issues

## Troubleshooting

### Invalid Ingestion Key
```
requests.exceptions.HTTPError: 401 Client Error: Unauthorized
```
**Solution**: Verify your `IBM_INGESTION_KEY` is correct and active.

### Wrong Endpoint
```
requests.exceptions.ConnectionError
```
**Solution**: Ensure you're using the correct regional endpoint for your LogDNA instance.

### Network Issues
If logs aren't appearing, check:
1. Your ingestion key is valid
2. The endpoint URL matches your instance region
3. Your network allows HTTPS traffic to IBM Cloud
4. The LogDNA instance is active and running

## Production Deployment

For production deployment on IBM Cloud:

1. **Cloud Foundry**: Use environment variables in manifest.yml
2. **Kubernetes Service**: Use ConfigMaps and Secrets
3. **Virtual Server**: Configure environment variables or use Key Protect
4. **Code Engine**: Set environment variables in the service configuration

### Example Cloud Foundry manifest.yml
```yaml
applications:
- name: flask-logging-app
  memory: 256M
  instances: 1
  env:
    IBM_INGESTION_KEY: ((logdna-key))
    IBM_LOG_ENDPOINT: logs.us-south.logging.cloud.ibm.com
    IBM_ENVIRONMENT: production
```

### Key Protect Integration
Store sensitive configuration in IBM Key Protect:

```bash
# Store ingestion key in Key Protect
ibmcloud kp key create logdna-ingestion-key \
  --instance-id your-key-protect-instance \
  --payload "your-ingestion-key"
```

## Advanced Features

### Custom Tags and Labels
Add custom tags to your logs for better organization:

```python
app.logger.info("Custom message", extra={
    'tags': ['user-action', 'purchase'],
    'labels': {
        'department': 'sales',
        'priority': 'high'
    }
})
```

### Structured Logging with Metadata
Include rich metadata for better log analysis:

```python
app.logger.info("Order processed", extra={
    'order': {
        'id': 'ORD-12345',
        'customer_id': 'CUST-789',
        'amount': 99.99,
        'currency': 'USD'
    },
    'processing_time_ms': 150,
    'ibm_transaction_id': 'TXN-ABC123'
})
```

## Additional Resources

- [IBM Cloud Logging Documentation](https://cloud.ibm.com/docs/log-analysis)
- [LogDNA REST API Documentation](https://docs.logdna.com/reference)
- [flask-remote-logging Documentation](../../README.md)
- [IBM Cloud CLI Reference](https://cloud.ibm.com/docs/cli)
