"""
Authentication routes for LinkedIn and Twitter OAuth
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
import secrets

from app.core.config import settings
from app.schemas.auth import ConnectionStatus, PlatformConnectionsStatus
from app.services.linkedin import linkedin_service
from app.services.twitter import twitter_service

router = APIRouter()

# In-memory state storage (use Redis in production)
oauth_states = {}
pkce_verifiers = {}


@router.get("/linkedin/connect")
async def linkedin_connect():
    """
    Initiate LinkedIn OAuth flow
    """
    state = secrets.token_urlsafe(32)
    oauth_states[state] = "linkedin"
    
    auth_url = linkedin_service.get_authorization_url(state)
    return {"authorization_url": auth_url, "state": state}


@router.get("/linkedin/callback")
async def linkedin_callback(code: str = Query(...), state: str = Query(...)):
    """
    LinkedIn OAuth callback
    """
    # Verify state
    if state not in oauth_states or oauth_states[state] != "linkedin":
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Remove used state
    del oauth_states[state]
    
    try:
        # Exchange code for tokens
        tokens = await linkedin_service.exchange_code_for_token(code)
        
        # In production, store tokens in database associated with user session
        # For now, return them (frontend should store securely)
        
        return {
            "success": True,
            "platform": "linkedin",
            "tokens": tokens,
            "message": "LinkedIn connected successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/twitter/connect")
async def twitter_connect():
    """
    Initiate Twitter OAuth flow with PKCE
    """
    state = secrets.token_urlsafe(32)
    code_verifier, code_challenge = twitter_service.generate_pkce_pair()
    
    oauth_states[state] = "twitter"
    pkce_verifiers[state] = code_verifier
    
    auth_url = twitter_service.get_authorization_url(state, code_challenge)
    return {"authorization_url": auth_url, "state": state}


@router.get("/twitter/callback")
async def twitter_callback(code: str = Query(...), state: str = Query(...)):
    """
    Twitter OAuth callback
    """
    # Verify state
    if state not in oauth_states or oauth_states[state] != "twitter":
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    if state not in pkce_verifiers:
        raise HTTPException(status_code=400, detail="PKCE verifier not found")
    
    code_verifier = pkce_verifiers[state]
    
    # Clean up
    del oauth_states[state]
    del pkce_verifiers[state]
    
    try:
        # Exchange code for tokens
        tokens = await twitter_service.exchange_code_for_token(code, code_verifier)
        
        return {
            "success": True,
            "platform": "twitter",
            "tokens": tokens,
            "message": "Twitter connected successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status", response_model=PlatformConnectionsStatus)
async def get_connection_status():
    """
    Get status of platform connections
    TODO: Implement proper user session and database lookup
    """
    # This is a placeholder - in production, check database for user's tokens
    return PlatformConnectionsStatus(
        linkedin=ConnectionStatus(
            platform="linkedin",
            connected=False,
            expires_at=None,
            username=None
        ),
        twitter=ConnectionStatus(
            platform="twitter",
            connected=False,
            expires_at=None,
            username=None
        )
    )


@router.post("/disconnect")
async def disconnect_platform(platform: str):
    """
    Disconnect a platform
    TODO: Implement proper user session and database update
    """
    if platform not in ["linkedin", "twitter"]:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    # In production: Delete tokens from database
    
    return {
        "success": True,
        "platform": platform,
        "message": f"{platform.capitalize()} disconnected successfully"
    }
