#!/bin/bash

# ScreenPilot Research Copilot Backend Service Startup Script

echo "Starting ScreenPilot Research Copilot Backend Service..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your actual API keys before running the service."
    echo "Required: OPENAI_API_KEY, FRIENDLIAI_API_KEY, WEAVIATE_URL"
    echo "This service supports PDF upload and analytical Q&A for research documents."
    exit 1
fi

# Start the service
echo "Starting FastAPI service..."
echo "Service will be available at: http://localhost:8000"
echo "API documentation: http://localhost:8000/docs"
echo "Press Ctrl+C to stop the service"
echo ""

python main.py
