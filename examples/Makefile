# Makefile for Flask Graylog Examples

.PHONY: help install run test-logging graylog-up graylog-down clean

# Default target
help:
	@echo "Flask Graylog Examples"
	@echo "====================="
	@echo ""
	@echo "Available commands:"
	@echo "  install        - Install dependencies"
	@echo "  run            - Run the example Flask application"
	@echo "  test-logging   - Run logging tests"
	@echo "  graylog-up     - Start Graylog services with Docker"
	@echo "  graylog-down   - Stop Graylog services"
	@echo "  quick-start    - Full setup and run (Graylog + Flask)"
	@echo "  clean          - Clean up generated files"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	pip3 install -r requirements.txt
	@if [ ! -f ".env" ]; then cp .env.example .env; echo "✅ Created .env file"; fi

# Run the Flask application
run: install
	@echo "🌶️ Starting Flask application..."
	@echo "📋 Application will be available at: http://127.0.0.1:5000"
	@echo "📋 Make sure Graylog is running (use 'make graylog-up')"
	python3 app.py

# Run logging tests
test-logging: install
	@echo "🧪 Running logging tests..."
	python3 test_logging.py

# Start Graylog services
graylog-up:
	@echo "🐳 Starting Graylog services with Docker Compose..."
	docker-compose up -d
	@echo "⏳ Waiting for services to start..."
	@sleep 10
	@echo "✅ Graylog services started!"
	@echo "📋 Graylog web interface: http://127.0.0.1:9000"
	@echo "📋 Login: admin / admin"
	@echo "📋 Remember to create a GELF UDP input on port 12201"

# Stop Graylog services
graylog-down:
	@echo "🛑 Stopping Graylog services..."
	docker-compose down
	@echo "✅ Graylog services stopped"

# Full quick start
quick-start:
	@echo "🚀 Flask Graylog Quick Start"
	@echo "==========================="
	@./run_example.sh

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@rm -f .env
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"
