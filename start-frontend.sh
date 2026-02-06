#!/bin/bash

echo "Starting Skinny Legend Frontend..."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
fi

# Start the dev server
echo "Starting Vite dev server on http://localhost:5173"
npm run dev
