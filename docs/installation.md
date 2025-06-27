# Installation Guide

This guide covers all the ways to install Flask Network Logging and its dependencies.

## Requirements

- Python 3.9 or higher
- Flask 1.1.4 or higher (but less than 2.0.0)

## Installation Methods

### 1. Basic Installation

Install the core package without any backend dependencies:

```bash
pip install flask-remote-logging
```

This gives you the base functionality but requires manual installation of backend-specific packages.

### 2. Backend-Specific Installation (Recommended)

Install with only the backends you need:

#### Graylog Support
```bash
pip install flask-remote-logging[graylog]
```
**Includes:** `pygelf` for GELF protocol support

#### AWS CloudWatch Support
```bash
pip install flask-remote-logging[aws]
```
**Includes:** `boto3`, `botocore` for AWS SDK

#### Google Cloud Logging Support
```bash
pip install flask-remote-logging[gcp]
```
**Includes:** `google-cloud-logging` for Cloud Logging API

#### Azure Monitor Support
```bash
pip install flask-remote-logging[azure]
```
**Includes:** `requests` for Azure REST API calls

#### IBM Cloud Logs Support
```bash
pip install flask-remote-logging[ibm]
```
**Includes:** `requests` for LogDNA ingestion API

#### Oracle Cloud Infrastructure Support
```bash
pip install flask-remote-logging[oci]
```
**Includes:** `oci` SDK for OCI Logging service

### 3. Multiple Backends

Install support for multiple backends:

```bash
# Common combinations
pip install flask-remote-logging[graylog,aws]
pip install flask-remote-logging[aws,gcp,azure]
pip install flask-remote-logging[graylog,aws,gcp,azure]
```

### 4. All Backends

Install support for all backends:

```bash
pip install flask-remote-logging[all]
```

**Includes all dependencies for:** Graylog, AWS, GCP, Azure, IBM, and OCI

## Development Installation

For contributing to the project:

```bash
# Clone the repository
git clone https://github.com/MarcFord/flask-remote-logging.git
cd flask-remote-logging

# Install in development mode with all dependencies
pip install -e .[all,dev]
```

## Dependency Details

### Core Dependencies

These are installed with any installation method:

- **Flask** (>=1.1.4, <2.0.0) - Web framework
- **user-agents** (>=2.0.0) - User agent parsing

### Optional Backend Dependencies

#### Graylog (`[graylog]`)
- **pygelf** - GELF (Graylog Extended Log Format) protocol support

#### AWS CloudWatch (`[aws]`)
- **boto3** - AWS SDK for Python
- **botocore** - Core AWS SDK functionality

#### Google Cloud Logging (`[gcp]`)
- **google-cloud-logging** - Google Cloud Logging client library

#### Azure Monitor (`[azure]`)
- **requests** - HTTP library for Azure REST API

#### IBM Cloud Logs (`[ibm]`)
- **requests** - HTTP library for LogDNA API

#### Oracle Cloud Infrastructure (`[oci]`)
- **oci** - Oracle Cloud Infrastructure SDK

## Installation Verification

### Verify Core Installation

```python
import flask_remote_logging
print(flask_remote_logging.__version__)
```

### Verify Backend Support

```python
# Test Graylog support
try:
    from flask_remote_logging import GraylogExtension
    print("✅ Graylog support available")
except ImportError as e:
    print(f"❌ Graylog support missing: {e}")

# Test AWS support
try:
    from flask_remote_logging import AWSLogExtension
    print("✅ AWS CloudWatch support available")
except ImportError as e:
    print(f"❌ AWS support missing: {e}")

# Test GCP support
try:
    from flask_remote_logging import GCPLogExtension
    print("✅ Google Cloud Logging support available")
except ImportError as e:
    print(f"❌ GCP support missing: {e}")

# Test Azure support
try:
    from flask_remote_logging import AzureLogExtension
    print("✅ Azure Monitor support available")
except ImportError as e:
    print(f"❌ Azure support missing: {e}")

# Test IBM support
try:
    from flask_remote_logging import IBMLogExtension
    print("✅ IBM Cloud Logs support available")
except ImportError as e:
    print(f"❌ IBM support missing: {e}")

# Test OCI support
try:
    from flask_remote_logging import OCILogExtension
    print("✅ Oracle Cloud Infrastructure support available")
except ImportError as e:
    print(f"❌ OCI support missing: {e}")
```

## Docker Installation

### Using Official Python Images

```dockerfile
FROM python:3.11-slim

# Install with specific backends
RUN pip install flask-remote-logging[graylog,aws]

COPY . /app
WORKDIR /app

CMD ["python", "app.py"]
```

### Multi-stage Build for Production

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user flask-remote-logging[graylog,aws]

# Production stage
FROM python:3.11-slim

# Copy installed packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . /app
WORKDIR /app

CMD ["python", "app.py"]
```

## Virtual Environment Setup

### Using venv

```bash
# Create virtual environment
python -m venv flask-logging-env

# Activate (Linux/Mac)
source flask-logging-env/bin/activate

# Activate (Windows)
flask-logging-env\Scripts\activate

# Install package
pip install flask-remote-logging[graylog]
```

### Using conda

```bash
# Create environment
conda create -n flask-logging python=3.11

# Activate environment
conda activate flask-logging

# Install package
pip install flask-remote-logging[graylog]
```

## Troubleshooting Installation

### Common Issues

#### 1. Missing Backend Dependencies

**Error:**
```
ImportError: No module named 'pygelf'
```

**Solution:**
```bash
pip install flask-remote-logging[graylog]
```

#### 2. Version Conflicts

**Error:**
```
ERROR: pip's dependency resolver does not currently have sufficient requirements to solve the dependency conflicts
```

**Solutions:**
```bash
# Use pip's legacy resolver
pip install --use-deprecated=legacy-resolver flask-remote-logging[all]

# Or upgrade pip first
pip install --upgrade pip
pip install flask-remote-logging[all]
```

#### 3. Permission Errors

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Install for current user only
pip install --user flask-remote-logging[graylog]

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install flask-remote-logging[graylog]
```

#### 4. SSL Certificate Issues

**Error:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solution:**
```bash
# Upgrade certificates (macOS)
/Applications/Python\ 3.x/Install\ Certificates.command

# Or use trusted hosts (temporary workaround)
pip install --trusted-host pypi.org --trusted-host pypi.python.org flask-remote-logging[graylog]
```

### Getting Help

If you encounter installation issues:

1. Check the [GitHub Issues](https://github.com/MarcFord/flask-remote-logging/issues)
2. Verify your Python version: `python --version`
3. Try installing in a fresh virtual environment
4. Check for conflicting packages: `pip list`

## Next Steps

After installation, continue with:

- **[Quick Start Guide](quickstart.md)** - Get logging working in minutes
- **[Configuration Reference](configuration.md)** - Understand all options
- **[User Guide](user_guide/index.md)** - Learn best practices
