# GitHub Actions CI/CD for flask-graylog

This document describes the complete CI/CD setup for the flask-graylog project.

## Overview

The CI/CD pipeline consists of three main workflows:

1. **Continuous Integration (`ci.yml`)** - Runs on every push and PR
2. **Release (`release.yml`)** - Runs on git tags to publish to PyPI
3. **Security Audit (`security.yml`)** - Runs weekly and on demand

## Continuous Integration

### Triggers
- Push to any branch
- Pull requests to main/master

### Jobs
1. **Test Matrix**
   - Python versions: 3.9, 3.10, 3.11, 3.12, 3.13
   - Operating systems: Ubuntu, Windows, macOS
   - Runs tests with coverage reporting

2. **Code Quality**
   - Black code formatting check
   - isort import sorting check
   - flake8 linting
   - mypy type checking
   - bandit security analysis

3. **Build**
   - Builds the Python package
   - Uploads build artifacts

### Features
- **Coverage reporting** to Codecov (from Ubuntu + Python 3.11)
- **Artifact upload** for dist files
- **Fast failure prevention** (matrix continues on single failure)
- **Multi-platform support** ensures compatibility

## Release Workflow

### Triggers
- Git tags matching `v*` pattern (e.g., `v1.0.0`)

### Process
1. **Validation**
   - Reuses the full CI workflow
   - Verifies version consistency between tag and package

2. **Publishing**
   - Builds the package
   - Publishes to PyPI using **Trusted Publishing** (OIDC)
   - No API tokens required!

3. **GitHub Release**
   - Creates GitHub release
   - Generates changelog from git commits
   - Links to PyPI package

### Trusted Publishing Setup

To enable trusted publishing:

1. **PyPI Configuration:**
   ```
   Go to: https://pypi.org/manage/account/publishing/
   Publisher: MarcFord/flask-graylog
   Environment: pypi
   ```

2. **GitHub Environment:**
   - Create environment named `pypi`
   - Add any protection rules as needed
   - No secrets required (uses OIDC)

## Security Workflow

### Triggers
- Weekly schedule (Mondays at 9:00 AM UTC)
- Manual dispatch

### Features
- **bandit** security code analysis
- **safety** dependency vulnerability scanning
- **Automated issue creation** if vulnerabilities found
- **Report artifacts** for investigation

## Additional Features

### Dependabot
- **Python dependencies** updated weekly
- **GitHub Actions** updated weekly
- Automatic PR creation with proper labels

### Issue Templates
- **Bug reports** with structured information
- **Feature requests** with problem/solution format

### Make Targets
Enhanced Makefile with CI/CD support:

```bash
make security      # Run security audit
make check-version  # Verify version consistency
make ci-test       # Run tests with XML coverage
make pre-release   # Full pre-release validation
```

## Release Process

### 1. Prepare Release
```bash
# Ensure everything is clean
make pre-release
make check-version
```

### 2. Version Bump
```bash
# Choose appropriate bump type
make release-patch  # Bug fixes (1.0.0 → 1.0.1)
make release-minor  # New features (1.0.0 → 1.1.0)
make release-major  # Breaking changes (1.0.0 → 2.0.0)
```

### 3. Create Release
```bash
# This triggers the entire release pipeline
make tag version=x.y.z
```

### 4. Automated Process
- CI runs full test suite
- Package is built and verified
- PyPI publish via trusted publishing
- GitHub release created with changelog

## Security Best Practices

### Code Security
- **bandit** scans for common security issues
- **# nosec** comments for justified suppressions
- Regular security audits via GitHub Actions

### Dependency Security
- **safety** scans for known vulnerabilities
- **Dependabot** keeps dependencies updated
- Automated issue creation for security alerts

### Supply Chain Security
- **Trusted publishing** eliminates API token risks
- **OIDC** authentication to PyPI
- **Signed releases** with provenance

## Monitoring and Maintenance

### Coverage Tracking
- **Codecov** integration for coverage reports
- Coverage badges in README
- Coverage requirements can be enforced

### Quality Gates
- All checks must pass before merge
- Matrix testing ensures cross-platform compatibility
- Security scans prevent vulnerable code

### Automation
- **Dependabot** for dependency updates
- **Scheduled security audits**
- **Automatic issue creation** for problems

This setup provides enterprise-grade CI/CD with comprehensive testing, security, and automation while maintaining simplicity for contributors.
