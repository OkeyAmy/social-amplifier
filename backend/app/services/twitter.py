"""
X (Twitter) API integration service using OAuth 2.0
"""
import httpx
from typing import Optional, Dict, List
import secrets
import hashlib
import base64

from urllib.parse import urlencode, quote

from app.core.config import settings
from app.core.security import encrypt_token, decrypt_token
from app.core.exceptions import PlatformConnectionError, TokenExpiredError, PublishingError, RateLimitError


class TwitterService:
    """Service for X (Twitter) API v2 interactions"""
    
    def __init__(self):
        self.client_id = settings.TWITTER_CLIENT_ID
        self.client_secret = settings.TWITTER_CLIENT_SECRET
        self.redirect_uri = settings.TWITTER_REDIRECT_URI
        self.auth_url = settings.TWITTER_AUTH_URL
        self.token_url = settings.TWITTER_TOKEN_URL
        self.api_url = settings.TWITTER_API_URL
    
    def generate_pkce_pair(self) -> tuple:
        """
        Generate PKCE code verifier and challenge for OAuth 2.0
        """
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
        code_verifier = code_verifier.replace('=', '')
        
        code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
        code_challenge = code_challenge.replace('=', '')
        
        return code_verifier, code_challenge
    
    def get_authorization_url(self, state: str, code_challenge: str, redirect_uri: Optional[str] = None) -> str:
        """
        Generate Twitter OAuth 2.0 authorization URL with PKCE
        """
        scopes = ["tweet.read", "tweet.write", "users.read", "offline.access"]
        scope_string = " ".join(scopes)
        redirect = (redirect_uri or self.redirect_uri or "").strip()

        if not redirect:
            raise PlatformConnectionError("Twitter redirect URI is not configured.")
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect,
            "scope": scope_string,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }

        query_string = urlencode(params, quote_via=quote)
        return f"{self.auth_url}?{query_string}"
    
    async def exchange_code_for_token(self, code: str, code_verifier: str, redirect_uri: Optional[str] = None) -> Dict:
        """
        Exchange authorization code for access token using PKCE
        """
        redirect = (redirect_uri or self.redirect_uri or "").strip()

        if not redirect:
            raise PlatformConnectionError("Twitter redirect URI is not configured.")

        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded"
                }

                if self.client_secret:
                    auth_string = f"{self.client_id}:{self.client_secret}"
                    auth_bytes = auth_string.encode('ascii')
                    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                    headers["Authorization"] = f"Basic {auth_b64}"

                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "authorization_code",
                        "client_id": self.client_id,
                        "code": code,
                        "redirect_uri": redirect,
                        "code_verifier": code_verifier
                    },
                    headers=headers
                )
                
                if response.status_code != 200:
                    try:
                        error_detail = response.json()
                    except ValueError:
                        error_detail = response.text
                    raise PlatformConnectionError(
                        f"Twitter OAuth failed ({response.status_code}): {error_detail}"
                    )
                
                data = response.json()
                
                # Encrypt tokens before storing
                return {
                    "access_token": encrypt_token(data["access_token"]),
                    "expires_in": data.get("expires_in", 7200),
                    "refresh_token": encrypt_token(data["refresh_token"]) if data.get("refresh_token") else None
                }
            
            except httpx.HTTPError as e:
                raise PlatformConnectionError(f"Failed to connect to Twitter: {str(e)}")
    
    async def get_user_profile(self, encrypted_access_token: str) -> Dict:
        """
        Retrieve user's Twitter profile
        """
        access_token = decrypt_token(encrypted_access_token)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_url}/users/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code == 401:
                    raise TokenExpiredError("Twitter access token expired")
                
                if response.status_code == 429:
                    raise RateLimitError("Twitter API rate limit exceeded")
                
                if response.status_code != 200:
                    raise PlatformConnectionError(f"Failed to fetch profile: {response.text}")
                
                return response.json()
            
            except httpx.HTTPError as e:
                raise PlatformConnectionError(f"Failed to fetch Twitter profile: {str(e)}")
    
    async def publish_tweet(
        self,
        encrypted_access_token: str,
        content: str,
        image_ids: Optional[List[str]] = None,
        reply_to_id: Optional[str] = None
    ) -> Dict:
        """
        Publish a single tweet
        """
        access_token = decrypt_token(encrypted_access_token)
        
        tweet_data = {"text": content}
        
        # Add image media IDs if provided
        if image_ids:
            tweet_data["media"] = {"media_ids": image_ids}
        
        # For thread replies
        if reply_to_id:
            tweet_data["reply"] = {"in_reply_to_tweet_id": reply_to_id}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_url}/tweets",
                    json=tweet_data,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code == 401:
                    raise TokenExpiredError("Twitter access token expired")
                
                if response.status_code == 429:
                    raise RateLimitError("Twitter API rate limit exceeded. Please wait before posting again.")
                
                if response.status_code not in [200, 201]:
                    raise PublishingError(f"Failed to publish tweet: {response.text}")
                
                return response.json()
            
            except httpx.HTTPError as e:
                raise PublishingError(f"Failed to publish tweet: {str(e)}")
    
    async def publish_thread(
        self,
        encrypted_access_token: str,
        tweets: List[str],
        image_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Publish a thread of tweets
        """
        results = []
        previous_tweet_id = None
        
        for i, tweet_text in enumerate(tweets):
            # Only attach images to first tweet
            media_ids = image_ids if i == 0 and image_ids else None
            
            result = await self.publish_tweet(
                encrypted_access_token,
                tweet_text,
                image_ids=media_ids,
                reply_to_id=previous_tweet_id
            )
            
            results.append(result)
            previous_tweet_id = result["data"]["id"]
        
        return results
    
    async def refresh_access_token(self, encrypted_refresh_token: str) -> Dict:
        """
        Refresh Twitter access token
        """
        refresh_token = decrypt_token(encrypted_refresh_token)
        
        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded"
                }

                if self.client_secret:
                    auth_string = f"{self.client_id}:{self.client_secret}"
                    auth_bytes = auth_string.encode('ascii')
                    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                    headers["Authorization"] = f"Basic {auth_b64}"

                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "refresh_token",
                        "client_id": self.client_id,
                        "refresh_token": refresh_token
                    },
                    headers=headers
                )
                
                if response.status_code != 200:
                    try:
                        error_detail = response.json()
                    except ValueError:
                        error_detail = response.text
                    raise TokenExpiredError(
                        f"Failed to refresh Twitter token ({response.status_code}): {error_detail}"
                    )
                
                data = response.json()
                
                return {
                    "access_token": encrypt_token(data["access_token"]),
                    "expires_in": data.get("expires_in", 7200),
                    "refresh_token": encrypt_token(data["refresh_token"]) if data.get("refresh_token") else None
                }
            
            except httpx.HTTPError as e:
                raise TokenExpiredError(f"Failed to refresh token: {str(e)}")


# Singleton instance
twitter_service = TwitterService()
