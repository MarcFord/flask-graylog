# Graylog Flask Example

This directory contains a complete Flask application example that demonstrates logging to Graylog using GELF (Graylog Extended Log Format).

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Graylog server details
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Visit the application:**
   - Open http://localhost:5000 in your browser
   - Check your Graylog web interface to see logs in real-time

## Configuration

Edit the `.env` file to configure your Graylog server:

- `GRAYLOG_HOST`: Your Graylog server hostname
- `GRAYLOG_PORT`: GELF UDP port (usually 12201)
- `GRAYLOG_LEVEL`: Minimum log level (DEBUG, INFO, WARNING, ERROR)
- `FLASK_REMOTE_LOGGING_ENVIRONMENT`: **Unified environment key** - Environment name for filtering
- `GRAYLOG_ENVIRONMENT`: *(Deprecated)* Legacy environment key - use `FLASK_REMOTE_LOGGING_ENVIRONMENT` instead

## Features Demonstrated

- **Request/Response logging**: Automatic logging of all HTTP requests
- **User context**: Simulated user information in logs
- **Different log levels**: DEBUG, INFO, WARNING, ERROR examples
- **Structured logging**: Complex nested data structures
- **Error handling**: Exception logging with stack traces
- **Bulk logging**: Performance testing with multiple log entries

## Testing Different Users

You can simulate different users by setting HTTP headers:

```bash
curl -H "X-User-ID: alice123" \
     -H "X-Username: alice" \
     -H "X-User-Email: alice@example.com" \
     http://localhost:5000/logs/user-context
```

## Endpoints

- `/` - Home page with API information
- `/health` - Health check endpoint
- `/users` - Mock users API
- `/logs/test` - Test different log levels
- `/logs/user-context` - User context logging
- `/logs/error` - Error logging with exceptions
- `/logs/bulk` - Bulk logging performance test
- `/logs/structured` - Complex structured data logging

All requests are automatically logged to Graylog with rich context information.
