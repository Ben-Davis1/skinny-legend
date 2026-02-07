#!/bin/bash

# Create necessary directories
mkdir -p uploads

# Create data directory if using persistent disk
if [ -n "$DATABASE_PATH" ]; then
    DB_DIR=$(dirname "$DATABASE_PATH")
    mkdir -p "$DB_DIR"
    echo "Using database at: $DATABASE_PATH"
fi

# Initialize database if it doesn't exist
DB_FILE="${DATABASE_PATH:-./skinny_legend.db}"
if [ ! -f "$DB_FILE" ]; then
    echo "Initializing database at $DB_FILE..."
    python3 -c "from database import init_db; init_db()"
else
    echo "Database already exists at $DB_FILE"
fi

# Start the application with gunicorn
exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 app:app
