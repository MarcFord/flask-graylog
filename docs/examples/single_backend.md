# Single Backend Examples

## Graylog Only

```python
from flask import Flask
from flask_remote_logging import RemoteLogging

app = Flask(__name__)

app.config['GRAYLOG_HOST'] = 'localhost'
app.config['GRAYLOG_PORT'] = 12201
app.config['GRAYLOG_FACILITY'] = 'flask-app'

network_logging = RemoteLogging()
network_logging.init_app(app)

@app.route('/')
def hello():
    app.logger.info('Hello endpoint called')
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
```

## AWS CloudWatch Only

```python
from flask import Flask
from flask_remote_logging import AWSLogExtension

app = Flask(__name__)

app.config['AWS_REGION'] = 'us-east-1'
app.config['AWS_LOG_GROUP'] = 'flask-app-logs'
app.config['AWS_LOG_STREAM'] = 'production'

aws_logging = AWSLogExtension()
aws_logging.init_app(app)

@app.route('/')
def hello():
    app.logger.info('Hello from AWS logging')
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
```
