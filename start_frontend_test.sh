#!/bin/bash

# Sahaaya Frontend Testing Script
echo "🏥 Sahaaya Universal Health System - Frontend Testing Guide"
echo "========================================================="

cd /Users/mabhila9/sahaaya_env/sahaaya-backend

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Activating virtual environment..."
    source /Users/mabhila9/sahaaya_env/bin/activate
fi

echo ""
echo "🚀 Starting Sahaaya test server on port 8080..."
echo ""

# Set environment variables
export PYTHONPATH=/Users/mabhila9/sahaaya_env/sahaaya-backend

# Start the server
echo "Starting server... (Press Ctrl+C to stop)"
echo ""
echo "📱 Frontend will be available at: http://localhost:8080/app"
echo "📚 API Documentation at: http://localhost:8080/docs"
echo "🔌 API Root at: http://localhost:8080/"
echo ""

/Users/mabhila9/sahaaya_env/bin/python -m uvicorn test_main:app --host 0.0.0.0 --port 8080