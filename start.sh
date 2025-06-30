#!/bin/bash

# Backend Docker startup script
set -e

echo "🚀 Starting Callback Listener Backend"

# Wait for database to be ready (if using external database)
if [[ "$DATABASE_URL" == postgresql* ]] || [[ "$DATABASE_URL" == mysql* ]]; then
    echo "⏳ Waiting for database to be ready..."
    sleep 10
fi

# Initialize database if it doesn't exist
echo "🗄️  Initializing database..."
python -c "
from app import create_app, db
import os

app = create_app()
with app.app_context():
    try:
        # Try to create tables if they don't exist
        db.create_all()
        print('✅ Database initialized successfully')
    except Exception as e:
        print(f'⚠️  Database initialization warning: {e}')
        # Continue anyway as tables might already exist
"

# Run database migrations if migrations directory exists
if [ -d "migrations" ]; then
    echo "🔄 Running database migrations..."
    python -c "
from flask_migrate import upgrade
from app import create_app

app = create_app()
with app.app_context():
    try:
        upgrade()
        print('✅ Database migrations completed')
    except Exception as e:
        print(f'⚠️  Migration warning: {e}')
        # Continue anyway
"
fi

echo "✅ Startup checks completed"
echo "🌐 Starting Gunicorn server..."

# Start the application
exec gunicorn --config gunicorn.conf.py run:app