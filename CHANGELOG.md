# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-27

### Added
- **NEW**: Google Cloud Logging support via `GCPLogExtension` and `GCPLog` alias
- Support for dual logging backends (Graylog + Google Cloud Logging)
- Example applications for GCP-only and dual logging configurations
- Comprehensive test coverage for GCP extension
- Enhanced documentation with both logging backends

### Changed
- **BREAKING**: Renamed package from `flask-graylog` to `flask-remote-logging`
- **BREAKING**: Main import path changed from `flask_graylog` to `flask_network_logging`
- Project scope expanded from Graylog-only to multiple remote logging services
- Package description updated to reflect broader scope
- All documentation updated for new project name and features

### Migration Guide

#### For existing users upgrading from flask-graylog:

**Before (v1.x):**
```python
from flask_graylog import Graylog
from flask_graylog import GraylogExtension
```

**After (v2.0+):**
```python
from flask_network_logging import Graylog  # Same alias
from flask_network_logging import GraylogExtension  # Same class
```

**New GCP functionality:**
```python
from flask_network_logging import GCPLog
from flask_network_logging import GCPLogExtension
```

### Technical Details
- All existing Graylog functionality preserved with backward-compatible aliases
- Test suite expanded from ~70 to 105+ tests
- CI/CD updated for new package structure
- Dependencies updated to include `google-cloud-logging`

## [1.0.2] - 2024-12-01

### Fixed
- Various bug fixes and improvements
- Enhanced error handling
- Performance optimizations

## [1.0.1] - 2024-11-15

### Fixed
- Documentation improvements
- Minor bug fixes

## [1.0.0] - 2024-11-01

### Added
- Initial release with Graylog support
- Flask integration via `GraylogExtension`
- Request context logging
- Configurable log levels and filtering
- Production-ready logging setup

[2.0.0]: https://github.com/MarcFord/flask-remote-logging/compare/v1.0.2...v2.0.0
[1.0.2]: https://github.com/MarcFord/flask-remote-logging/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/MarcFord/flask-remote-logging/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/MarcFord/flask-remote-logging/releases/tag/v1.0.0
