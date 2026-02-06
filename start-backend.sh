#!/bin/bash

echo "Starting Skinny Legend Backend..."

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
if [ ! -f "venv/.deps_installed" ]; then
    echo "Installing dependencies..."
    pip install --upgrade pip setuptools wheel > /dev/null 2>&1
    pip install Flask Flask-CORS python-dotenv requests Pillow anthropic
    touch venv/.deps_installed
    echo "✓ Dependencies installed"
else
    echo "✓ Dependencies already installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo ""
    echo "WARNING: Please edit backend/.env and add your ANTHROPIC_API_KEY"
    echo ""
fi

# Initialize database if it doesn't exist
if [ ! -f "skinny_legend.db" ]; then
    echo "Initializing database..."
    python3 -c "from database import init_db; init_db()"
fi

# Start the server
echo "Starting Flask server on http://localhost:8000"
python3 app.py
