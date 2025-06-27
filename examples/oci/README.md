# Oracle Cloud Infrastructure (OCI) Logging Flask Example

This example demonstrates how to integrate Flask with Oracle Cloud Infrastructure Logging using the `flask-remote-logging` package.

## Features

- **OCI Logging Integration**: Send logs directly to OCI Logging service
- **Request Context Logging**: Automatic logging of request details with correlation IDs
- **Structured Logging**: JSON-formatted logs with custom fields and metadata
- **Performance Monitoring**: Log request timing and performance metrics
- **Error Handling**: Comprehensive error logging with stack traces
- **Health Checks**: Built-in health check endpoint with OCI metadata

## Prerequisites

1. **Oracle Cloud Account**: You need an active Oracle Cloud Infrastructure account
2. **OCI CLI Setup**: Install and configure the OCI CLI
3. **Log Group and Log**: Create a Log Group and Log in OCI Logging service
4. **Proper IAM Policies**: Ensure your user/instance has permission to write logs

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install and Configure OCI CLI** (if not already done):
   ```bash
   # Install OCI CLI
   bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
   
   # Configure OCI CLI
   oci setup config
   ```

3. **Create Log Group and Log** (if not exists):
   ```bash
   # Create a Log Group
   oci logging log-group create \
     --compartment-id ocid1.compartment.oc1..your-compartment-id \
     --display-name "Flask App Log Group"
   
   # Create a Log
   oci logging log create \
     --log-group-id ocid1.loggroup.oc1..your-log-group-id \
     --display-name "Flask App Log" \
     --log-type CUSTOM
   ```

4. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your OCI resource OCIDs
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```

## Configuration

The application can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OCI_CONFIG_FILE` | Path to OCI config file | `~/.oci/config` |
| `OCI_CONFIG_PROFILE` | OCI config profile name | `DEFAULT` |
| `OCI_LOG_GROUP_ID` | Log Group OCID | `ocid1.loggroup.oc1..your-log-group-id` |
| `OCI_LOG_ID` | Log OCID | `ocid1.log.oc1..your-log-id` |
| `OCI_COMPARTMENT_ID` | Compartment OCID | `ocid1.compartment.oc1..your-compartment-id` |
| `OCI_LOG_SOURCE_NAME` | Log source identifier | `flask-oci-example` |
| `OCI_LOG_LEVEL` | Logging level | `INFO` |
| `OCI_ENVIRONMENT` | Environment name | `development` |
| `PORT` | Server port | `5000` |

## API Endpoints

- `GET /` - Home page with API information
- `GET /health` - Health check with OCI metadata
- `GET /users` - Mock users API with structured logging
- `GET /logs/test` - Test different log levels
- `GET /logs/user-context` - Test user context logging
- `GET /logs/error` - Test error logging and exception handling
- `GET /logs/oci-metrics` - Test OCI-specific metrics and structured logging
- `GET /logs/performance` - Test performance logging with timing

## Usage Examples

### Test Basic Logging
```bash
curl http://localhost:5000/logs/test
```

### Test User Context (with OCI headers)
```bash
curl -H "X-User-ID: alice123" \
     -H "X-Username: alice" \
     -H "X-User-Email: alice@example.com" \
     -H "X-OCI-User-OCID: ocid1.user.oc1..alice123" \
     -H "X-OCI-Tenancy-OCID: ocid1.tenancy.oc1..tenancy123" \
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

You can view the logs in OCI Console:

1. Go to [OCI Console](https://cloud.oracle.com)
2. Navigate to "Observability & Management" → "Logging" → "Logs"
3. Select your compartment and log group
4. View your custom log to see the application logs

### OCI CLI Log Search
You can also search logs using the OCI CLI:

```bash
# Search logs from the last hour
oci logging-search search-logs \
  --search-query "search \"ocid1.compartment.oc1..your-compartment-id/ocid1.loggroup.oc1..your-log-group-id/ocid1.log.oc1..your-log-id\" | sort by datetime desc" \
  --time-start $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S.000Z) \
  --time-end $(date -u +%Y-%m-%dT%H:%M:%S.000Z)

# Search for error logs
oci logging-search search-logs \
  --search-query "search \"ocid1.compartment.oc1..your-compartment-id/ocid1.loggroup.oc1..your-log-group-id/ocid1.log.oc1..your-log-id\" | where data.level = 'ERROR' | sort by datetime desc"
```

### Log Search Examples

**Search for request completion logs:**
```
search "your-compartment-id/your-log-group-id/your-log-id" | where data.message = "Request completed" | sort by datetime desc
```

**Search for error logs:**
```
search "your-compartment-id/your-log-group-id/your-log-id" | where data.level = "ERROR" | sort by datetime desc
```

**Search by request ID:**
```
search "your-compartment-id/your-log-group-id/your-log-id" | where data.request_id = "specific-request-id" | sort by datetime desc
```

**Performance analysis:**
```
search "your-compartment-id/your-log-group-id/your-log-id" | where data.duration_ms is not null | sort by data.duration_ms desc
```

## Development

For local development, the application will:
- Log to both OCI Logging and console (stdout)
- Include detailed request context and timing
- Show helpful error messages for configuration issues

## Troubleshooting

### Authentication Issues
```
oci.exceptions.ConfigFileNotFound: Could not find config file at ~/.oci/config
```
**Solution**: Run `oci setup config` to create the configuration file.

### Permission Issues
```
oci.exceptions.ServiceError: Authorization failed or requested resource not found
```
**Solution**: Ensure your user has the necessary IAM policies:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "LOG_ANALYTICS_LOG_GROUP_UPLOAD_LOGS"
      ],
      "Resource": "ocid1.loggroup.oc1..your-log-group-id"
    }
  ]
}
```

### Invalid OCIDs
```
oci.exceptions.ServiceError: Invalid parameter value
```
**Solution**: Verify that your Log Group and Log OCIDs are correct and exist in the specified compartment.

## Production Deployment

For production deployment on OCI:

1. **Compute Instances**: Use instance principals for authentication
2. **Container Engine (OKE)**: Use service accounts with proper RBAC
3. **Functions**: Configure function-level IAM policies
4. **API Gateway**: Set up appropriate logging policies

### Instance Principal Authentication

For Compute instances, you can use instance principals instead of API keys:

```python
# In your application, you can use instance principal auth
app.config.update({
    'OCI_USE_INSTANCE_PRINCIPAL': True,  # This would be a custom config option
    # ... other config
})
```

Create a dynamic group and policy for your instances:

```bash
# Create dynamic group
oci iam dynamic-group create \
  --name "flask-app-instances" \
  --description "Instances running Flask app" \
  --matching-rule "ANY {instance.compartment.id = 'ocid1.compartment.oc1..your-compartment-id'}"

# Create policy
oci iam policy create \
  --name "flask-app-logging-policy" \
  --description "Allow Flask app instances to write logs" \
  --statements '["allow dynamic-group flask-app-instances to use log-content in compartment id ocid1.compartment.oc1..your-compartment-id"]' \
  --compartment-id ocid1.compartment.oc1..your-tenancy-id
```

## Advanced Features

### Custom Log Sources
You can create multiple log sources for different parts of your application:

```python
app.logger.info("Database operation", extra={
    'log_source': 'database',
    'operation': 'user_query',
    'duration_ms': 45.2
})

app.logger.info("API call", extra={
    'log_source': 'external_api',
    'endpoint': 'https://api.example.com/users',
    'status_code': 200
})
```

### Structured Logging with OCI Context
Include rich OCI context in your logs:

```python
app.logger.info("Resource operation", extra={
    'oci_resource': {
        'type': 'compute_instance',
        'ocid': 'ocid1.instance.oc1.iad.instance123',
        'compartment_id': 'ocid1.compartment.oc1..compartment123',
        'availability_domain': 'AD-1',
        'fault_domain': 'FAULT-DOMAIN-1'
    },
    'operation': 'backup_created',
    'backup_ocid': 'ocid1.bootvolume.oc1.iad.backup123'
})
```

## Additional Resources

- [OCI Logging Documentation](https://docs.oracle.com/en-us/iaas/Content/Logging/home.htm)
- [OCI CLI Documentation](https://docs.oracle.com/en-us/iaas/tools/oci-cli/3.22.3/oci_cli_docs/)
- [OCI Python SDK Documentation](https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/)
- [flask-remote-logging Documentation](../../README.md)
- [OCI IAM Policies for Logging](https://docs.oracle.com/en-us/iaas/Content/Identity/Reference/loggingpolicyreference.htm)
