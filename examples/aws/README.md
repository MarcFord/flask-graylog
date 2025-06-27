# AWS CloudWatch Logs Flask Example

This directory contains a complete Flask application example that demonstrates logging to AWS CloudWatch Logs.

## Quick Start

1. **Configure AWS credentials:**
   - Use AWS CLI: `aws configure`
   - Or use IAM roles (recommended for EC2/Lambda/ECS)
   - Or set environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS settings
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Visit the application:**
   - Open http://localhost:5000 in your browser
   - Check AWS CloudWatch Logs console to see logs in real-time

## AWS Configuration

Edit the `.env` file to configure your AWS CloudWatch Logs:

- `AWS_REGION`: AWS region (e.g., us-east-1)
- `AWS_LOG_GROUP`: CloudWatch log group name
- `AWS_LOG_STREAM`: CloudWatch log stream name
- `AWS_LOG_LEVEL`: Minimum log level (DEBUG, INFO, WARNING, ERROR)
- `AWS_ENVIRONMENT`: Environment name for filtering
- `AWS_CREATE_LOG_GROUP`: Auto-create log group if it doesn't exist
- `AWS_CREATE_LOG_STREAM`: Auto-create log stream if it doesn't exist

## Required AWS Permissions

Your AWS credentials need the following CloudWatch Logs permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

## Features Demonstrated

- **Request/Response logging**: Automatic logging of all HTTP requests
- **AWS context**: AWS-specific metadata and request IDs
- **User context**: AWS user ARNs and IAM context
- **Different log levels**: DEBUG, INFO, WARNING, ERROR examples
- **Performance metrics**: AWS-specific performance logging
- **Error handling**: Exception logging with AWS context
- **CloudWatch integration**: Native AWS CloudWatch Logs format

## Testing Different Users

You can simulate different AWS users by setting HTTP headers:

```bash
curl -H "X-User-ID: alice123" \
     -H "X-Username: alice" \
     -H "X-User-Email: alice@company.com" \
     -H "X-AWS-User-ARN: arn:aws:iam::123456789012:user/alice" \
     http://localhost:5000/logs/user-context
```

## Endpoints

- `/` - Home page with API information
- `/health` - Health check with AWS metadata
- `/users` - Mock users API
- `/logs/test` - Test different log levels
- `/logs/user-context` - AWS user context logging
- `/logs/error` - Error logging with AWS context
- `/logs/aws-metrics` - AWS-specific system metrics
- `/logs/performance` - Performance logging

## CloudWatch Logs Integration

All logs are sent to AWS CloudWatch Logs with:
- Automatic log group/stream creation
- AWS region and service context
- Request tracing with AWS X-Ray compatibility
- Structured JSON logging
- Error correlation and alerting capabilities

## Deployment to AWS

This example works great when deployed to:
- **AWS EC2**: Use IAM roles for authentication
- **AWS Lambda**: Automatic CloudWatch Logs integration
- **AWS ECS/Fargate**: Use task roles for authentication
- **AWS EKS**: Use service accounts with IAM roles
