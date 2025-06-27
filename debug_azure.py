#!/usr/bin/env python3

"""Debug script to test Azure extension setup."""

from flask import Flask
from src.flask_remote_logging import AzureLogExtension

app = Flask(__name__)
app.config.update({
    'AZURE_WORKSPACE_ID': 'test-id',
    'AZURE_WORKSPACE_KEY': 'test-key',
    'AZURE_LOG_TYPE': 'TestLogs',
    'AZURE_ENVIRONMENT': 'azure'
})

print("Before initialization:")
print(f"before_request_funcs: {app.before_request_funcs}")
print(f"after_request_funcs: {app.after_request_funcs}")

extension = AzureLogExtension(app, enable_middleware=True)

print("\nAfter initialization:")
print(f"before_request_funcs: {app.before_request_funcs}")
print(f"after_request_funcs: {app.after_request_funcs}")

print(f"\nExtension details:")
print(f"enable_middleware: {extension.enable_middleware}")
print(f"_logging_setup: {extension._logging_setup}")

# Check if _setup_logging was called
print("\nTrying to call _setup_logging manually:")
extension._setup_logging()

print("\nAfter manual setup:")
print(f"before_request_funcs: {app.before_request_funcs}")
print(f"after_request_funcs: {app.after_request_funcs}")
