"""
Pydantic schemas for authentication-related requests and responses
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[int] = None
    email: Optional[str] = None


class ConnectionStatus(BaseModel):
    """Platform connection status"""
    platform: str
    connected: bool
    expires_at: Optional[datetime] = None
    username: Optional[str] = None


class PlatformConnectionsStatus(BaseModel):
    """Status of all platform connections"""
    linkedin: ConnectionStatus
    twitter: ConnectionStatus


class OAuthCallbackRequest(BaseModel):
    """OAuth callback parameters"""
    code: str
    state: Optional[str] = None


class DisconnectRequest(BaseModel):
    """Disconnect platform request"""
    platform: str  # 'linkedin' or 'twitter'
