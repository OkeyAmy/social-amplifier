@echo off
REM Social Amplifier Backend - Quick Start Script for Windows

echo Starting Social Amplifier Backend...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3 is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo .env file not found. Creating from .env.example...
    copy .env.example .env
    echo .env file created. Please edit it with your API keys before continuing.
    echo.
    echo Required keys:
    echo   - GEMINI_API_KEY
    echo   - LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET
    echo   - TWITTER_CLIENT_ID and TWITTER_CLIENT_SECRET
    echo.
    pause
)

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Initialize database
echo Initializing database...
python -m app.database.init_db

REM Start the server
echo.
echo Setup complete!
echo Starting server at http://localhost:8000
echo API docs will be available at http://localhost:8000/docs
echo.

python main.py
