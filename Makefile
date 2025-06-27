# Makefile for flask-graylog package

.PHONY: help test lint format build tag clean install-dev install-tools pre-release security check-version ci-test

# Default target
help:
	@echo "Available commands:"
	@echo "  test           - Run tests with coverage"
	@echo "  lint           - Run code quality checks"
	@echo "  format         - Format code with black and isort"
	@echo "  build          - Build the package"
	@echo "  install-dev    - Install development dependencies"
	@echo "  install-tools  - Install development tools (black, isort, etc.)"
	@echo "  tag            - Create and push a git tag (usage: make tag version=1.0.0)"
	@echo "  clean          - Clean build artifacts"
	@echo "  pre-release    - Run all checks before release"
	@echo "  security       - Run security audit (bandit + safety)"
	@echo "  check-version  - Verify package version from git"
	@echo "  ci-test        - Run tests in CI mode (with XML coverage)"

# Test the package
test:
	uv run pytest --cov=src/flask_remote_logging --cov-report=term-missing -v

# Run linting
lint:
	uv tool run black --check --diff src/ tests/ --line-length 120
	uv tool run isort --check-only --diff src/ tests/ --profile black --line-length 120
	uv tool run flake8 src/ --max-line-length=120 --extend-ignore=E203,W503
	uv tool run mypy src/flask_remote_logging/ --python-version 3.9 --ignore-missing-imports
	uv tool run bandit -r src/flask_remote_logging/

# Format code
format:
	uv tool run black src/ tests/ --line-length 120
	uv tool run isort src/ tests/ --profile black --line-length 120

# Build the package
build:
	uv build

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf src/*.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

# Release commands
release-patch:
	@echo "Creating patch release..."
	python scripts/bump_version.py patch

release-minor:
	@echo "Creating minor release..."
	python scripts/bump_version.py minor

release-major:
	@echo "Creating major release..."
	python scripts/bump_version.py major

# Create and push a git tag
tag:
ifndef version
	@echo "❌ Error: version argument is required"
	@echo "Usage: make tag version=1.0.0"
	@exit 1
endif
	@echo "Creating and pushing tag v$(version)..."
	git tag v$(version)
	git push origin v$(version)
	@echo "✅ Tag v$(version) created and pushed successfully!"
	@echo "📦 Version will be automatically derived from git tag"

# Install development dependencies
install-dev:
	uv sync --all-extras

# Install development tools
install-tools:
	uv tool install black
	uv tool install isort
	uv tool install flake8
	uv tool install mypy
	uv tool install bandit

# Run all checks before release
pre-release: test lint
	@echo "✅ All checks passed! Ready for release."

# Run security audit
security:
	@echo "Running security audit..."
	uv tool run bandit -r src/flask_remote_logging/
	uv tool install safety
	uv tool run safety scan

# Check version consistency
check-version:
	@echo "Checking version from git tags..."
	@python -c "import src.flask_remote_logging; \
		package_version = src.flask_remote_logging.__version__; \
		print(f'Package version (from git): {package_version}'); \
		print('⚠️  Development version detected (no git tags)' if package_version.endswith('-dev') else '✅ Version successfully derived from git tags!')"

# Run tests in CI mode (with XML coverage)
ci-test:
	uv run pytest --cov=src/flask_remote_logging --cov-report=xml --cov-report=term-missing -v
