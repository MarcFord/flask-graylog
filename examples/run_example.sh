#!/bin/bash

# Flask Graylog Example - Quick Start Script
#
# This script helps you quickly set up and run the Flask Graylog example application.
# It will start Graylog using Docker Compose and then run the Flask application.

set -e

echo "🚀 Flask Graylog Example - Quick Start"
echo "====================================="

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Step 1: Start Graylog services
echo "📦 Starting Graylog services with Docker Compose..."
docker-compose up -d

echo "⏳ Waiting for Graylog to start up (this may take 1-2 minutes)..."
sleep 30

# Check if Graylog is ready
echo "🔍 Checking if Graylog is ready..."
max_attempts=12
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s -f http://127.0.0.1:9000/api/system/cluster/health > /dev/null 2>&1; then
        echo "✅ Graylog is ready!"
        break
    else
        echo "⏳ Attempt $attempt/$max_attempts - Graylog not ready yet, waiting..."
        sleep 10
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ Graylog failed to start after $max_attempts attempts"
    echo "   Please check the Docker logs: docker-compose logs graylog"
    exit 1
fi

# Step 2: Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
else
    echo "❌ requirements.txt not found. Please run this script from the examples directory."
    exit 1
fi

# Step 3: Set up environment variables
echo ""
echo "⚙️ Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from .env.example"
else
    echo "✅ .env file already exists"
fi

# Step 4: Start the Flask application
echo ""
echo "🌶️ Starting Flask application..."
echo ""
echo "📋 Quick Setup Summary:"
echo "   • Graylog web interface: http://127.0.0.1:9000"
echo "   • Login: admin / admin"
echo "   • Flask app will start on: http://127.0.0.1:5000"
echo ""
echo "🔧 Next steps after Flask starts:"
echo "   1. Open http://127.0.0.1:9000 in your browser"
echo "   2. Login with username 'admin' and password 'admin'"
echo "   3. Go to System/Inputs and create a GELF UDP input on port 12201"
echo "   4. Test the Flask app endpoints to see logs in Graylog"
echo ""
echo "🧪 Test endpoints:"
echo "   • curl http://127.0.0.1:5000/log-test"
echo "   • curl http://127.0.0.1:5000/simulate-error"
echo "   • curl http://127.0.0.1:5000/users"
echo ""
echo "Press Ctrl+C to stop the Flask application"
echo "Run 'docker-compose down' to stop Graylog services"
echo ""

# Export environment variables and run Flask app
export FLASK_ENV=development
export FLASK_DEBUG=true
python3 app.py
