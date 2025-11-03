#!/bin/bash
# =============================================================================
# Docker Entrypoint Script for Social Amplifier Backend
# =============================================================================
# This script ensures database initialization happens before starting the app
# =============================================================================

set -e  # Exit on any error (except for database init which we handle gracefully)

echo "🚀 Starting Social Amplifier Backend..."
echo ""

# Initialize database tables if they don't exist
# We handle errors gracefully here since database might already be initialized
echo "🗄️  Initializing database..."
python -c "
import asyncio
import sys
from app.database.init_db import init_database

async def main():
    try:
        await init_database()
        print('✅ Database initialized successfully!')
    except Exception as e:
        print(f'⚠️  Database initialization warning: {e}')
        print('Continuing anyway...')
        sys.exit(0)  # Exit with success even if init fails

asyncio.run(main())
" || {
    echo "⚠️  Database initialization skipped (will be created on first use)"
}

echo ""
echo "✅ Starting application server..."
echo ""

# Execute the main command (uvicorn)
exec "$@"

