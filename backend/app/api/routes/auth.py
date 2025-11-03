"""
Authentication routes for LinkedIn and Twitter OAuth
"""
import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Query, Request

from app.schemas.auth import PlatformConnectionsStatus
from app.services.linkedin import linkedin_service
from app.services.twitter import twitter_service
from app.services.user_connections import user_connection_service

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory state storage (use Redis in production)
oauth_states = {}
pkce_verifiers = {}

def _calculate_expiry(expires_in: Optional[int]) -> Optional[datetime]:
    """Convert an expires_in value (seconds) into an absolute UTC datetime."""
    if not expires_in:
        return None

    try:
        return datetime.utcnow() + timedelta(seconds=int(expires_in))
    except (TypeError, ValueError):
        logger.warning("Invalid expires_in value received: %s", expires_in)
        return None
@router.get("/linkedin/connect")
async def linkedin_connect(request: Request):
    """
    Initiate LinkedIn OAuth flow
    """
    state = secrets.token_urlsafe(32)
    oauth_states[state] = "linkedin"

    redirect_uri = str(request.url_for("linkedin_callback"))
    auth_url = linkedin_service.get_authorization_url(state, redirect_uri=redirect_uri)
    return {"authorization_url": auth_url, "state": state, "redirect_uri": redirect_uri}


@router.get("/linkedin/callback")
async def linkedin_callback(request: Request, code: str = Query(...), state: str = Query(...)):
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
        redirect_uri = str(request.url_for("linkedin_callback"))
        tokens = await linkedin_service.exchange_code_for_token(code, redirect_uri=redirect_uri)

        expires_at = _calculate_expiry(tokens.get("expires_in"))
        profile_data: Optional[Dict[str, Any]] = None
        username: Optional[str] = None

        try:
            profile_data = await linkedin_service.get_user_profile(tokens["access_token"])
            if profile_data:
                first_name = profile_data.get("localizedFirstName")
                last_name = profile_data.get("localizedLastName")
                vanity_name = profile_data.get("vanityName")

                if first_name or last_name:
                    username = " ".join(
                        part for part in [first_name, last_name] if part
                    ).strip() or None
                if not username and vanity_name:
                    username = vanity_name
        except Exception as profile_error:  # pragma: no cover - best effort only
            logger.warning("Failed to fetch LinkedIn profile: %s", profile_error)

        status = await user_connection_service.update_linkedin_connection(
            tokens=tokens,
            expires_at=expires_at,
            username=username,
            member_id=profile_data.get("id") if profile_data else None,
        )

        return {
            "success": True,
            "platform": "linkedin",
            "tokens": tokens,
            "message": "LinkedIn connected successfully",
            "username": status.username,
            "expires_at": status.expires_at,
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/twitter/connect")
async def twitter_connect(request: Request):
    """
    Initiate Twitter OAuth flow with PKCE
    """
    state = secrets.token_urlsafe(32)
    code_verifier, code_challenge = twitter_service.generate_pkce_pair()
    
    oauth_states[state] = "twitter"
    pkce_verifiers[state] = code_verifier

    redirect_uri = str(request.url_for("twitter_callback"))
    auth_url = twitter_service.get_authorization_url(state, code_challenge, redirect_uri=redirect_uri)
    return {"authorization_url": auth_url, "state": state, "redirect_uri": redirect_uri}


@router.get("/twitter/callback")
async def twitter_callback(request: Request, code: str = Query(...), state: str = Query(...)):
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
        redirect_uri = str(request.url_for("twitter_callback"))
        tokens = await twitter_service.exchange_code_for_token(code, code_verifier, redirect_uri=redirect_uri)

        expires_at = _calculate_expiry(tokens.get("expires_in"))
        profile_data: Optional[Dict[str, Any]] = None
        username: Optional[str] = None
        user_id: Optional[str] = None

        try:
            profile_data = await twitter_service.get_user_profile(tokens["access_token"])
            if profile_data:
                data = profile_data.get("data") or {}
                username = data.get("username") or data.get("name")
                user_id = data.get("id")
        except Exception as profile_error:  # pragma: no cover - best effort only
            logger.warning("Failed to fetch Twitter profile: %s", profile_error)

        status = await user_connection_service.update_twitter_connection(
            tokens=tokens,
            expires_at=expires_at,
            username=username,
            user_id=user_id,
        )

        return {
            "success": True,
            "platform": "twitter",
            "tokens": tokens,
            "message": "Twitter connected successfully",
            "username": status.username,
            "expires_at": status.expires_at,
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status", response_model=PlatformConnectionsStatus)
async def get_connection_status():
    """
    Get status of platform connections
    TODO: Implement proper user session and database lookup
    """
    return await user_connection_service.get_connection_status()


@router.post("/disconnect")
async def disconnect_platform(platform: str):
    """
    Disconnect a platform
    TODO: Implement proper user session and database update
    """
    if platform not in ["linkedin", "twitter"]:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    status = await user_connection_service.disconnect(platform)

    return {
        "success": True,
        "platform": platform,
        "message": f"{platform.capitalize()} disconnected successfully",
        "status": status,
    }
