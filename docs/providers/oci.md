# Oracle Cloud Infrastructure Logging

Send logs to Oracle Cloud Infrastructure (OCI) Logging service.

## Installation

```bash
pip install flask-remote-logging[oci]
```

## Configuration

```python
from flask import Flask
from flask_remote_logging import OCILogExtension

app = Flask(__name__)

# OCI configuration
app.config['OCI_CONFIG_FILE'] = '~/.oci/config'
app.config['OCI_CONFIG_PROFILE'] = 'DEFAULT'
app.config['OCI_LOG_GROUP_ID'] = 'ocid1.loggroup.oc1...'
app.config['OCI_LOG_ID'] = 'ocid1.log.oc1...'

oci_logging = OCILogExtension()
oci_logging.init_app(app)
```

## OCI Configuration

### Config File Setup

Create `~/.oci/config` with your OCI credentials:

```ini
[DEFAULT]
user=ocid1.user.oc1..aaaaa
fingerprint=aa:bb:cc:dd:ee:ff
key_file=~/.oci/oci_api_key.pem
tenancy=ocid1.tenancy.oc1..aaaaa
region=us-ashburn-1
```

### Getting Log IDs

1. Create a Log Group in OCI Console
2. Create a Log within the Log Group  
3. Copy the OCIDs for both resources

## Required Permissions

Your OCI user/group needs the `LOG_GROUP_LOGS_WRITE` permission for the target log group.
