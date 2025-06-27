# Multi-Backend Logging Flask Example

This example demonstrates how to integrate Flask with multiple cloud logging services simultaneously using the `flask-remote-logging` package. This approach is ideal for multi-cloud deployments, backup logging strategies, service migrations, and centralized log aggregation.

## Supported Backends

- **Graylog** (GELF protocol)
- **AWS CloudWatch Logs**
- **Google Cloud Logging**
- **Azure Monitor Logs** (Log Analytics)
- **IBM Cloud Logging** (LogDNA)
- **Oracle Cloud Infrastructure (OCI) Logging**

## Features

- **Multi-Backend Logging**: Send logs to multiple services simultaneously
- **Flexible Configuration**: Enable/disable backends independently
- **Unified User Context**: Track users across all cloud providers
- **Request Correlation**: Maintain request IDs across all backends
- **Performance Monitoring**: Track logging performance across backends
- **Error Handling**: Comprehensive error logging with backend status
- **Stress Testing**: Built-in stress test endpoint for all backends

## Use Cases

1. **Multi-Cloud Deployments**: Log to multiple cloud providers for redundancy
2. **Cloud Migration**: Gradually migrate from one logging backend to another
3. **Backup Logging**: Use secondary backends as backup in case primary fails
4. **Compliance**: Meet requirements for logging to specific providers
5. **Analytics**: Aggregate logs across different cloud services

## Prerequisites

Depending on which backends you want to use, you'll need:

- **Graylog**: Running Graylog instance
- **AWS**: AWS account with CloudWatch Logs permissions
- **GCP**: Google Cloud project with Cloud Logging API enabled
- **Azure**: Azure subscription with Log Analytics workspace
- **IBM**: IBM Cloud account with LogDNA instance
- **OCI**: Oracle Cloud account with Logging service

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env to enable and configure the backends you want to use
   ```

3. **Enable Backends** (edit `.env`):
   ```bash
   # Enable the backends you want to use
   GRAYLOG_ENABLE=true
   AWS_ENABLE=true
   GCP_ENABLE=true
   # ... configure other backends as needed
   ```

4. **Configure Backend Credentials** (see individual backend documentation):
   - [Graylog](../graylog/README.md)
   - [AWS](../aws/README.md)
   - [GCP](../gcp/README.md)
   - [Azure](../azure/README.md)
   - [IBM](../ibm/README.md)
   - [OCI](../oci/README.md)

5. **Run the Application**:
   ```bash
   python app.py
   ```

## Configuration

The application uses a unified configuration system where each backend can be enabled independently:

### Global Configuration
| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Global logging level | `INFO` |
| `ENVIRONMENT` | Environment name | `development` |
| `PORT` | Server port | `5000` |

### Backend Enable Flags
| Variable | Description |
|----------|-------------|
| `GRAYLOG_ENABLE` | Enable Graylog backend |
| `AWS_ENABLE` | Enable AWS CloudWatch backend |
| `GCP_ENABLE` | Enable Google Cloud Logging backend |
| `AZURE_ENABLE` | Enable Azure Monitor Logs backend |
| `IBM_ENABLE` | Enable IBM Cloud Logging backend |
| `OCI_ENABLE` | Enable OCI Logging backend |

### Example Configurations

**Hybrid Cloud (AWS + On-Premises Graylog):**
```bash
GRAYLOG_ENABLE=true
GRAYLOG_HOST=graylog.company.com

AWS_ENABLE=true
AWS_LOG_GROUP=/aws/flask-app/logs
```

**Multi-Cloud Redundancy:**
```bash
AWS_ENABLE=true
GCP_ENABLE=true
AZURE_ENABLE=true
```

**Development + Production:**
```bash
GRAYLOG_ENABLE=true  # Development
AWS_ENABLE=true      # Production
```

## API Endpoints

- `GET /` - Home page with backend status and API information
- `GET /health` - Health check with all backend information
- `GET /users` - Mock users API with structured logging
- `GET /logs/test` - Test different log levels across all backends
- `GET /logs/user-context` - Test user context logging with multi-cloud data
- `GET /logs/error` - Test error logging and exception handling
- `GET /logs/backend-test` - Test backend-specific features and metadata
- `GET /logs/performance` - Test performance logging with multi-backend timing
- `GET /logs/stress` - Stress test all backends with multiple log entries

## Usage Examples

### Test Multi-Backend Logging
```bash
curl http://localhost:5000/logs/test
```

### Test Multi-Cloud User Context
```bash
curl -H "X-User-ID: alice123" \
     -H "X-Username: alice" \
     -H "X-User-Email: alice@example.com" \
     -H "X-AWS-User-ARN: arn:aws:iam::123456789012:user/alice" \
     -H "X-GCP-User-Email: alice@company.com" \
     -H "X-MS-CLIENT-PRINCIPAL-NAME: alice@company.com" \
     -H "X-IBM-User-ID: alice@company.com" \
     -H "X-OCI-User-OCID: ocid1.user.oc1..alice123" \
     http://localhost:5000/logs/user-context
```

### Stress Test All Backends
```bash
curl http://localhost:5000/logs/stress
```

### Check Backend Status
```bash
curl http://localhost:5000/health
```

## Viewing Logs

Logs will be sent to all enabled backends simultaneously. You can view them in:

- **Graylog**: Graylog web interface
- **AWS**: CloudWatch Logs console
- **GCP**: Cloud Logging console
- **Azure**: Log Analytics workspace
- **IBM**: LogDNA dashboard
- **OCI**: OCI Logging console

### Log Correlation

All logs include a `request_id` field that can be used to correlate logs across backends:

**Example log search across providers:**
- **AWS CloudWatch**: Filter by `request_id`
- **GCP**: `jsonPayload.request_id="abc-123"`
- **Azure**: `request_id_s == "abc-123"`

## Performance Considerations

### Latency Impact
- Each enabled backend adds to the total logging latency
- Backends are called sequentially during log emission
- Consider async logging for high-throughput applications

### Resource Usage
- Memory usage increases with the number of backends
- Network bandwidth scales with backend count
- Monitor application performance with multiple backends

### Optimization Tips
1. **Selective Enablement**: Only enable backends you actually need
2. **Log Level Filtering**: Use appropriate log levels to reduce volume
3. **Batch Logging**: Consider batching for high-volume applications
4. **Health Monitoring**: Monitor backend health and disable failing backends

## Error Handling

The application handles backend failures gracefully:

- Failed backend initialization doesn't prevent app startup
- Individual backend errors don't affect other backends
- Backend status is tracked and reported via `/health` endpoint
- Logs continue to be sent to healthy backends

### Backend Status Monitoring

Check backend health via the health endpoint:

```bash
curl http://localhost:5000/health | jq '.backends'
```

Response includes:
```json
{
  "backends": {
    "enabled": ["AWS CloudWatch", "Google Cloud Logging"],
    "count": 2,
    "status": {
      "aws": {"enabled": true, "status": "configured"},
      "gcp": {"enabled": true, "status": "configured"},
      "azure": {"enabled": false, "error": "Missing credentials"}
    }
  }
}
```

## Troubleshooting

### No Backends Enabled
```
⚠️ No backends enabled. Check your environment configuration!
```
**Solution**: Set at least one `*_ENABLE=true` and provide the required credentials.

### Backend Initialization Failures
Check the backend status in the health endpoint to see specific error messages.

### High Latency
If logging latency is high:
1. Reduce the number of enabled backends
2. Increase log level to reduce volume
3. Check network connectivity to backend services
4. Monitor backend service health

### Memory Issues
If memory usage is high:
1. Disable unused backends
2. Reduce log retention in application
3. Monitor for memory leaks in backend libraries

## Production Deployment

### Security Considerations
- Store sensitive credentials in secure vaults (AWS Secrets Manager, Azure Key Vault, etc.)
- Use environment-specific configurations
- Implement proper access controls for log data
- Monitor for credential exposure in logs

### Monitoring
- Set up alerts for backend failures
- Monitor logging performance and latency
- Track log volume across backends
- Implement log sampling for high-volume applications

### Scaling
- Consider async logging for high-throughput applications
- Use connection pooling for backend clients
- Implement circuit breakers for failing backends
- Monitor resource usage and scale accordingly

## Advanced Scenarios

### Cloud Migration
Gradually migrate from one backend to another:

```bash
# Phase 1: Enable both old and new backends
OLD_BACKEND_ENABLE=true
NEW_BACKEND_ENABLE=true

# Phase 2: Verify logs in new backend
# Phase 3: Disable old backend
OLD_BACKEND_ENABLE=false
NEW_BACKEND_ENABLE=true
```

### Compliance Logging
Meet compliance requirements by logging to specific providers:

```bash
# EU compliance: Use EU-based backends
AZURE_ENABLE=true  # EU regions
GCP_ENABLE=true    # EU regions

# US compliance: Use US-based backends
AWS_ENABLE=true    # US regions
IBM_ENABLE=true    # US regions
```

### Multi-Tenant Scenarios
Configure different backends for different tenants by using tenant-specific configuration.

## Additional Resources

- [flask-remote-logging Documentation](../../README.md)
- [Individual Backend Examples](../)
- [Graylog Example](../graylog/README.md)
- [AWS Example](../aws/README.md)
- [GCP Example](../gcp/README.md)
- [Azure Example](../azure/README.md)
- [IBM Example](../ibm/README.md)
- [OCI Example](../oci/README.md)
