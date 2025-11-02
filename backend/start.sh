#!/bin/bash

# Social Amplifier Backend - Quick Start Script

echo "🚀 Starting Social Amplifier Backend..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your API keys before continuing."
    echo ""
    echo "Required keys:"
    echo "  - GEMINI_API_KEY (Get from: https://makersuite.google.com/app/apikey)"
    echo "  - LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET"
    echo "  - TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET"
    echo ""
    read -p "Press enter once you've configured .env file..."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python -m app.database.init_db

# Start the server
echo ""
echo "✅ Setup complete!"
echo "🌐 Starting server at http://localhost:8000"
echo "📖 API docs will be available at http://localhost:8000/docs"
echo ""

python main.py
