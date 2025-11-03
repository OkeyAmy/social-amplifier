"""
Configuration management for the Social Amplifier backend
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Server Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # LinkedIn OAuth
    LINKEDIN_CLIENT_ID: str = os.getenv("LINKEDIN_CLIENT_ID", "")
    LINKEDIN_CLIENT_SECRET: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    LINKEDIN_REDIRECT_URI: str = os.getenv("LINKEDIN_REDIRECT_URI", "")
    LINKEDIN_AUTH_URL: str = "https://www.linkedin.com/oauth/v2/authorization"
    LINKEDIN_TOKEN_URL: str = "https://www.linkedin.com/oauth/v2/accessToken"
    LINKEDIN_API_URL: str = "https://api.linkedin.com/v2"
    
    # X (Twitter) OAuth 2.0
    TWITTER_CLIENT_ID: str = os.getenv("TWITTER_CLIENT_ID", "")
    TWITTER_CLIENT_SECRET: str = os.getenv("TWITTER_CLIENT_SECRET", "")
    TWITTER_REDIRECT_URI: str = os.getenv("TWITTER_REDIRECT_URI", "")
    TWITTER_AUTH_URL: str = "https://twitter.com/i/oauth2/authorize"
    TWITTER_TOKEN_URL: str = "https://api.twitter.com/2/oauth2/token"
    TWITTER_API_URL: str = "https://api.twitter.com/2"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./social_amplifier.db")
    
    # CORS - Leave as str for now, converted to List[str] after instantiation
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:8080,http://127.0.0.1:8080"
    
    # Session Configuration
    SESSION_TIMEOUT_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Normalize `CORS_ORIGINS` into a List[str]
DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

cors_raw = settings.CORS_ORIGINS or ""
if isinstance(cors_raw, str):
    cors_value = cors_raw.strip()
    if not cors_value:
        origins = DEFAULT_CORS_ORIGINS
    else:
        try:
            import json
            parsed = json.loads(cors_value)
            origins = parsed if isinstance(parsed, list) else [p.strip() for p in cors_value.split(",") if p.strip()]
        except Exception:
            origins = [p.strip() for p in cors_value.split(",") if p.strip()]
else:
    origins = cors_raw if isinstance(cors_raw, list) else DEFAULT_CORS_ORIGINS

# Convert back to ensure type consistency
settings.CORS_ORIGINS = origins  # type: ignore
