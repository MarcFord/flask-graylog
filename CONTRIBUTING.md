# Contributing to flask-graylog

Thank you for your interest in contributing to flask-graylog! This guide will help you get started.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MarcFord/flask-graylog.git
   cd flask-graylog
   ```

2. **Install dependencies:**
   ```bash
   make install-dev
   make install-tools
   ```

3. **Run tests:**
   ```bash
   make test
   ```

## Development Workflow

### Code Quality
We maintain high code quality standards. Before submitting a PR:

```bash
# Format code
make format

# Run all quality checks
make lint

# Run tests
make test

# Run security audit
make security

# Run all pre-release checks
make pre-release
```

### Testing
- Write tests for new features and bug fixes
- Ensure all tests pass: `make test`
- Test coverage should remain high
- Tests run automatically on all Python versions 3.9+ in CI

### Code Style
- We use `black` for code formatting (120 character line limit)
- `isort` for import sorting
- `flake8` for linting
- `mypy` for type checking
- `bandit` for security analysis

All formatting and linting is enforced in CI.

## CI/CD Pipeline

### Continuous Integration
Our CI pipeline runs on every push and pull request:

- **Multi-platform testing:** Ubuntu, Windows, macOS
- **Multi-version testing:** Python 3.9, 3.10, 3.11, 3.12, 3.13
- **Code quality checks:** black, isort, flake8, mypy, bandit
- **Security auditing:** bandit, safety
- **Coverage reporting:** Codecov integration

### Continuous Deployment
Releases are automated when you push a git tag:

1. **Create a release:**
   ```bash
   # Bump version in pyproject.toml and __init__.py
   make release-patch  # or release-minor, release-major
   
   # Create and push tag
   make tag version=1.0.0
   ```

2. **Automated process:**
   - Full test suite runs
   - Package is built
   - Version consistency is verified
   - Package is published to PyPI using trusted publishing
   - GitHub release is created with changelog

### Security
- **Weekly security audits:** Automated dependency vulnerability scanning
- **Dependabot:** Automated dependency updates
- **Security issue creation:** Automatic GitHub issues for vulnerabilities

## Release Process

The release process uses automatic versioning from git tags with `setuptools-scm`:

1. **Prepare release:**
   ```bash
   # Ensure all tests pass
   make pre-release
   
   # Check version from git
   make check-version
   ```

2. **Create release:**
   ```bash
   # Create and push tag (triggers automated release pipeline)
   make tag version=x.y.z
   ```

3. **Automated process:**
   - Full test suite runs
   - Package is built with version automatically derived from git tag
   - Package is published to PyPI using trusted publishing
   - GitHub release is created with changelog

### Version Management

- **No manual version files**: Versions are automatically derived from git tags
- **Development versions**: Show as `x.y.z-dev` when working from non-tagged commits
- **Release versions**: Automatically match the git tag (e.g., `v1.0.0` → `1.0.0`)

## PyPI Trusted Publishing Setup

To set up trusted publishing for PyPI:

1. **Configure PyPI:**
   - Go to https://pypi.org/manage/account/publishing/
   - Add publisher for `MarcFord/flask-graylog`
   - Environment: `pypi`

2. **Repository settings:**
   - Create environment named `pypi`
   - Add protection rules as needed
   - No secrets required (uses OIDC)

## Pull Request Guidelines

1. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes:**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Test locally:**
   ```bash
   make pre-release
   ```

4. **Submit PR:**
   - Fill out the PR template
   - Link any related issues
   - Ensure CI passes

## Issue Guidelines

Please use our issue templates:
- **Bug reports:** Include version info, reproduction steps, and error logs
- **Feature requests:** Describe the problem and proposed solution

## Getting Help

- **Issues:** GitHub issues for bugs and feature requests
- **Discussions:** GitHub discussions for questions and ideas
- **Security:** Email security issues privately to the maintainers
