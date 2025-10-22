#!/bin/bash

# ScreenPilot Research Copilot - Startup Script
# This script helps you get the ScreenPilot backend running quickly

echo "🚀 ScreenPilot Research Copilot - Startup Script"
echo "================================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Navigate to server directory
cd "$(dirname "$0")/server"

echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file from template"
        echo "📝 Please edit .env file with your actual API keys:"
        echo "   - FRIENDLIAI_API_KEY"
        echo "   - OPENAI_API_KEY"
        echo "   - WEAVIATE_URL (or start local Weaviate)"
        echo "   - GEMINI_API_KEY (optional)"
    else
        echo "❌ .env.example template not found"
        exit 1
    fi
fi

# Check if Weaviate is running (optional)
echo "🔍 Checking Weaviate connection..."
if curl -s http://localhost:8080/v1/meta > /dev/null 2>&1; then
    echo "✅ Weaviate is running on localhost:8080"
else
    echo "⚠️  Weaviate not detected on localhost:8080"
    echo "   To start Weaviate locally, run:"
    echo "   docker run -p 8080:8080 weaviate/weaviate:latest"
    echo ""
    echo "   Or update WEAVIATE_URL in .env to point to your Weaviate instance"
fi

echo ""
echo "🎯 Starting ScreenPilot backend server..."
echo "   Server will be available at: http://localhost:8000"
echo "   Health check: http://localhost:8000/health"
echo "   API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 main.py