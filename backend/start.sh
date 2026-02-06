#!/bin/bash

# Create necessary directories
mkdir -p uploads

# Initialize database if it doesn't exist
if [ ! -f "skinny_legend.db" ]; then
    echo "Initializing database..."
    python3 -c "from database import init_db; init_db()"
fi

# Start the application with gunicorn
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 app:app
