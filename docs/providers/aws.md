# AWS CloudWatch Logs

Send logs to Amazon CloudWatch Logs service.

## Installation

```bash
pip install flask-remote-logging[aws]
```

## Configuration

```python
from flask import Flask
from flask_remote_logging import AWSLogExtension

app = Flask(__name__)

# AWS configuration
app.config['AWS_REGION'] = 'us-east-1'
app.config['AWS_LOG_GROUP'] = 'my-flask-app'
app.config['AWS_LOG_STREAM'] = 'production'

# Credentials (optional if using IAM roles)
app.config['AWS_ACCESS_KEY_ID'] = 'your-access-key'
app.config['AWS_SECRET_ACCESS_KEY'] = 'your-secret-key'

aws_logging = AWSLogExtension()
aws_logging.init_app(app)
```

## IAM Permissions

Your AWS credentials need the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```
