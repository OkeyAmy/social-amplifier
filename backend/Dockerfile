# =============================================================================
# Social Amplifier Backend - Production Dockerfile for Render.com
# =============================================================================
# This Dockerfile creates a production-ready container for the FastAPI backend
# It includes all dependencies, database initialization, and proper security
# =============================================================================

# Stage 1: Base image with Python 3.11
# Using slim variant for smaller image size while maintaining compatibility
FROM python:3.11-slim as base

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install system dependencies required for Python packages and database operations
# build-essential: Required for compiling some Python packages (cryptography, etc.)
# libpq-dev: PostgreSQL client library (for asyncpg if using PostgreSQL)
# gcc: C compiler for Python extensions
# libffi-dev: Required for cryptography package
# libssl-dev: SSL development libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Dependencies installation
FROM base as dependencies

# Set working directory
WORKDIR /app

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy requirements file first (for better Docker layer caching)
COPY requirements.txt .

# Upgrade pip to latest version for better package management
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies from requirements.txt
# Using --no-cache-dir to reduce image size
# Installing system dependencies for Pillow (image processing)
# Keep curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*

# Stage 3: Application build
FROM dependencies as application

# Set working directory
WORKDIR /app

# Copy all application files
# Note: .dockerignore should exclude unnecessary files
COPY --chown=appuser:appuser . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Switch to non-root user for security
USER appuser

# Expose the port that the application runs on
# Render.com will map this to their own port
EXPOSE 8000

# Health check to ensure the container is running properly
# This helps Render.com and other platforms monitor container health
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set entrypoint script
# This script handles database initialization before starting the app
ENTRYPOINT ["./entrypoint.sh"]

# Default command to run the application
# Using uvicorn directly for production (no auto-reload)
# The host 0.0.0.0 allows external connections
# workers=1 for Render.com free tier (adjust based on your instance size)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

# =============================================================================
# Notes for Render.com Deployment:
# =============================================================================
# 1. Environment Variables Required (set in Render.com dashboard):
#    - SECRET_KEY: Generate with: openssl rand -hex 32
#    - ENCRYPTION_KEY: Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
#    - GEMINI_API_KEY: Your Google Gemini API key
#    - LINKEDIN_CLIENT_ID: LinkedIn OAuth client ID
#    - LINKEDIN_CLIENT_SECRET: LinkedIn OAuth client secret
#    - LINKEDIN_REDIRECT_URI: Your LinkedIn callback URL
#    - TWITTER_CLIENT_ID: Twitter OAuth client ID
#    - TWITTER_CLIENT_SECRET: Twitter OAuth client secret
#    - TWITTER_REDIRECT_URI: Your Twitter callback URL
#    - TWITTER_CONSUMER_KEY: Twitter consumer key (if using OAuth 1.0a)
#    - TWITTER_CONSUMER_SECRET: Twitter consumer secret (if using OAuth 1.0a)
#    - DATABASE_URL: For SQLite (default): sqlite+aiosqlite:///./social_amplifier.db
#                    For PostgreSQL: postgresql+asyncpg://user:password@host:5432/dbname
#    - CORS_ORIGINS: Comma-separated list of allowed origins
#    - DEBUG: Set to False for production
#    - API_HOST: Leave as default (0.0.0.0)
#    - API_PORT: Leave as default (8000)
#
# 2. Database Setup:
#    - For SQLite: Database file will be created in /app directory (persistent if using volumes)
#    - For PostgreSQL: Install asyncpg in requirements.txt: pip install asyncpg
#    - Database tables are auto-created on first startup via init_db.py
#
# 3. Render.com Configuration:
#    - Build Command: docker build -t social-amplifier-backend ./backend
#    - Start Command: (handled by Dockerfile CMD)
#    - Port: 8000 (as exposed in Dockerfile)
#    - Health Check Path: /health (already configured in main.py)
#
# 4. Security Best Practices:
#    - Never commit .env files to version control
#    - Use Render.com's environment variable encryption
#    - Regularly update dependencies for security patches
#    - Use non-root user (already configured: appuser)
#    - Enable HTTPS in Render.com settings
#
# 5. Monitoring:
#    - Health endpoint: GET /health
#    - API docs: GET /docs (Swagger UI)
#    - ReDoc: GET /redoc
#
# 6. Performance Optimization:
#    - Adjust --workers flag based on Render.com instance size
#    - For smaller instances: --workers 1
#    - For larger instances: --workers 4 (adjust based on CPU cores)
#    - Consider using PostgreSQL for production instead of SQLite
# =============================================================================

