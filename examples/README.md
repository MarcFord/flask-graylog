# Flask Graylog Example Application

This directory contains a comprehensive example application demonstrating how to use the flask-graylog extension in a real Flask application.

## Features Demonstrated

### Core Functionality
- ✅ **Graylog Integration**: Complete setup with environment-based configuration
- ✅ **Multiple Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ **Custom Fields**: Additional context data in log messages
- ✅ **Request Context**: Automatic logging of request/response information
- ✅ **Error Handling**: Comprehensive error logging with stack traces

### Example Endpoints
- `/` - Home page with API documentation
- `/users` - List all users with logging
- `/users/<id>` - Get specific user (with 404 handling)
- `/products` - List all products
- `/products/<id>` - Get specific product (with 404 handling)
- `/log-test` - Test all log levels
- `/simulate-error` - Demonstrate error logging
- `/health` - Health check endpoint

### Advanced Features
- **Before/After Request Hooks**: Performance tracking and request logging
- **Error Handlers**: Custom 404 and 500 error handling
- **Environment Configuration**: Easy deployment configuration
- **Custom Extra Fields**: Service metadata in all logs

## Quick Start

### 1. Install Dependencies

```bash
# From the examples directory
pip install -r requirements.txt

# Or if using the development version
cd ..
pip install -e .
cd examples
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your Graylog server details
# GRAYLOG_HOST=your-graylog-server.com
# GRAYLOG_PORT=12201
```

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://127.0.0.1:5000`

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_HOST` | Flask server host | `127.0.0.1` |
| `FLASK_PORT` | Flask server port | `5000` |
| `FLASK_DEBUG` | Enable Flask debug mode | `true` |
| `FLASK_ENV` | Flask environment | `development` |
| `GRAYLOG_HOST` | Graylog server hostname | `localhost` |
| `GRAYLOG_PORT` | Graylog GELF UDP port | `12201` |
| `GRAYLOG_LEVEL` | Minimum log level | `INFO` |
| `GRAYLOG_ENVIRONMENT` | Environment name for filtering | `development` |
| `GRAYLOG_FACILITY` | Facility name for grouping | `flask-example` |
| `DATACENTER` | Datacenter identifier | `local` |

### Application Configuration

The example shows how to configure the flask-graylog extension:

```python
app.config.update({
    'GRAYLOG_HOST': os.getenv('GRAYLOG_HOST', 'localhost'),
    'GRAYLOG_PORT': int(os.getenv('GRAYLOG_PORT', 12201)),
    'GRAYLOG_LEVEL': os.getenv('GRAYLOG_LEVEL', 'INFO'),
    'GRAYLOG_ENVIRONMENT': os.getenv('GRAYLOG_ENVIRONMENT', 'development')
})
```

## Usage Examples

### Basic Logging

```python
# Simple info log
app.logger.info("User login successful")

# Log with extra fields
app.logger.info("User action")
```

### Error Handling

```python
try:
    # Some operation
    result = risky_operation()
except Exception as e:
    app.logger.error(e)
```

## Testing the Example

### 1. Test Different Log Levels
```bash
curl http://127.0.0.1:5000/log-test
```

### 2. Test Error Handling
```bash
curl http://127.0.0.1:5000/simulate-error
```

### 3. Test Warning Scenarios
```bash
curl http://127.0.0.1:5000/simulate-warning
```

### 4. Test 404 Handling
```bash
curl http://127.0.0.1:5000/nonexistent
```

### 5. Test API Endpoints
```bash
# List users
curl http://127.0.0.1:5000/users

# Get specific user
curl http://127.0.0.1:5000/users/1

# List products
curl http://127.0.0.1:5000/products
```

## Graylog Setup

### Docker Compose Example

If you don't have a Graylog server running, you can use this Docker Compose setup for testing:

```yaml
version: '3'
services:
  mongodb:
    image: mongo:4.2
    networks:
      - graylog
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch-oss:7.10.2
    environment:
      - discovery.type=single-node
    networks:
      - graylog
  graylog:
    image: graylog/graylog:4.2
    environment:
      - GRAYLOG_PASSWORD_SECRET=somepasswordpepper
      - GRAYLOG_ROOT_PASSWORD_SHA2=8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918
      - GRAYLOG_HTTP_EXTERNAL_URI=http://127.0.0.1:9000/
    networks:
      - graylog
    ports:
      - 9000:9000
      - 12201:12201/udp
    depends_on:
      - mongodb
      - elasticsearch

networks:
  graylog:
    driver: bridge
```

### Accessing Graylog

1. Start with: `docker-compose up -d`
2. Access web interface: `http://127.0.0.1:9000`
3. Login: username `admin`, password `admin`
4. Configure GELF UDP input on port 12201

## Log Message Structure

The extension automatically adds context to your log messages:

```json
{
  "version": "1.1",
  "host": "hostname",
  "short_message": "Your log message",
  "full_message": "Your log message with details",
  "timestamp": 1234567890.123,
  "level": 6,
  "_service": "flask-graylog-example",
  "_version": "1.0.0",
  "_request_id": "req-123",
  "_user_agent": "Mozilla/5.0...",
  "_remote_addr": "127.0.0.1"
}
```

## Best Practices Demonstrated

1. **Structured Logging**: Use extra fields for searchable metadata
2. **Request Tracking**: Log request start/end with performance metrics
3. **Error Context**: Include relevant context in error logs
4. **Environment Configuration**: Use environment variables for deployment
5. **Log Levels**: Use appropriate log levels for different scenarios
6. **Custom Fields**: Add service metadata for filtering and analysis

## Production Considerations

1. **Log Level**: Set `GRAYLOG_LEVEL=WARNING` or `ERROR` in production
2. **Environment Filtering**: Use `GRAYLOG_ENVIRONMENT` to control log flow
3. **Performance**: Monitor logging overhead in high-traffic applications
4. **Security**: Don't log sensitive information (passwords, tokens, etc.)
5. **Storage**: Configure Graylog retention policies for log management
