# Google Cloud Logging Flask Example

This example demonstrates how to integrate Flask with Google Cloud Logging using the `flask-remote-logging` package.

## Features

- **Google Cloud Logging Integration**: Send logs directly to Google Cloud Logging
- **Request Context Logging**: Automatic logging of request details with correlation IDs
- **Structured Logging**: JSON-formatted logs with custom fields and metadata
- **Performance Monitoring**: Log request timing and performance metrics
- **Error Handling**: Comprehensive error logging with stack traces
- **Health Checks**: Built-in health check endpoint with GCP metadata

## Prerequisites

1. **Google Cloud Project**: You need a GCP project with Cloud Logging API enabled
2. **Authentication**: Either default credentials (if running on GCP) or a service account JSON file
3. **Permissions**: The service account needs `Logging Writer` role

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your GCP project details
   ```

3. **Set up Authentication** (choose one):
   
   **Option A: Default Credentials (recommended for GCP environments)**
   ```bash
   gcloud auth application-default login
   ```
   
   **Option B: Service Account JSON**
   ```bash
   export GCP_CREDENTIALS_PATH=/path/to/service-account.json
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```

## Configuration

The application can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `GCP_PROJECT_ID` | Google Cloud project ID | `your-gcp-project-id` |
| `GCP_CREDENTIALS_PATH` | Path to service account JSON (optional) | None |
| `GCP_LOG_NAME` | Cloud Logging log name | `flask-gcp-example` |
| `GCP_LOG_LEVEL` | Logging level | `INFO` |
| `GCP_ENVIRONMENT` | Environment name | `development` |
| `PORT` | Server port | `5000` |

## API Endpoints

- `GET /` - Home page with API information
- `GET /health` - Health check with GCP metadata
- `GET /users` - Mock users API with structured logging
- `GET /logs/test` - Test different log levels
- `GET /logs/user-context` - Test user context logging
- `GET /logs/error` - Test error logging and exception handling
- `GET /logs/gcp-metrics` - Test GCP-specific metrics and structured logging
- `GET /logs/performance` - Test performance logging with timing

## Usage Examples

### Test Basic Logging
```bash
curl http://localhost:5000/logs/test
```

### Test User Context (with custom headers)
```bash
curl -H "X-User-ID: alice123" \
     -H "X-Username: alice" \
     -H "X-User-Email: alice@example.com" \
     -H "X-GCP-User-Email: alice@company.com" \
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

You can view the logs in Google Cloud Console:

1. Go to [Cloud Logging](https://console.cloud.google.com/logs)
2. Filter by log name: `flask-gcp-example`
3. Or use the filter: `logName="projects/YOUR_PROJECT_ID/logs/flask-gcp-example"`

## Development

For local development, the application will:
- Log to both Google Cloud Logging and console (stdout)
- Include detailed request context and timing
- Show helpful error messages for configuration issues

## Troubleshooting

### Authentication Issues
```
google.auth.exceptions.DefaultCredentialsError: Could not automatically determine credentials
```
**Solution**: Set up authentication using `gcloud auth application-default login` or provide a service account JSON file.

### Permission Issues
```
google.api_core.exceptions.PermissionDenied: The caller does not have permission
```
**Solution**: Ensure your service account has the `Logging Writer` role.

### Project Not Found
```
google.api_core.exceptions.NotFound: Project not found
```
**Solution**: Verify your `GCP_PROJECT_ID` is correct and the project exists.

## Production Deployment

For production deployment on Google Cloud:

1. **App Engine**: Default credentials work automatically
2. **Compute Engine**: Assign appropriate service account to the instance
3. **Cloud Run**: Set the service account with logging permissions
4. **GKE**: Use Workload Identity for secure authentication

## Additional Resources

- [Google Cloud Logging Documentation](https://cloud.google.com/logging/docs)
- [flask-remote-logging Documentation](../../README.md)
- [Google Cloud Authentication Guide](https://cloud.google.com/docs/authentication)
