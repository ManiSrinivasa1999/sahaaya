#!/bin/bash

# Sahaaya Universal Health System - Development Server Startup
# This script starts both the backend API and serves the frontend

echo "🏥 Starting Sahaaya Universal Health System v1.2"
echo "================================================"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Please activate your virtual environment first:"
    echo "   source /Users/mabhila9/sahaaya_env/bin/activate"
    exit 1
fi

# Change to backend directory
cd "$(dirname "$0")"

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the server
echo "🚀 Starting Sahaaya server..."
echo "   API: http://localhost:8000"
echo "   Frontend: http://localhost:8000/app"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🌍 Features available:"
echo "   ✅ Urban Mode: AI-enhanced guidance"
echo "   ✅ Rural Mode: Complete offline functionality" 
echo "   ✅ Emergency Protocols: Immediate life-saving guidance"
echo "   ✅ Multilingual: 5 Indian languages supported"
echo "   ✅ PWA: Mobile app-like experience"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000