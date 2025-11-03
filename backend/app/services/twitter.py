"""
X (Twitter) API integration service using OAuth 2.0
"""
import asyncio
import httpx
import requests
from typing import Optional, Dict, List
import secrets
import hashlib
import base64

from urllib.parse import urlencode, quote

from requests_oauthlib import OAuth1

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
        self.consumer_key = settings.TWITTER_CONSUMER_KEY
        self.consumer_secret = settings.TWITTER_CONSUMER_SECRET
    
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
        
        tweet_data = {"text": content}
        
        # Add image media IDs if provided
        if image_ids:
            tweet_data["media"] = {"media_ids": image_ids}
        
        # For thread replies
        if reply_to_id:
            tweet_data["reply"] = {"in_reply_to_tweet_id": reply_to_id}
        
        oauth = self._get_oauth1(encrypted_access_token)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        def _post_tweet() -> requests.Response:
            return requests.post(
                url="https://api.x.com/2/tweets",
                json=tweet_data,
                headers=headers,
                auth=oauth,
            )

        response: requests.Response = await asyncio.to_thread(_post_tweet)

        if response.status_code == 401:
            raise TokenExpiredError("Twitter access token expired")

        if response.status_code == 429:
            raise RateLimitError("Twitter API rate limit exceeded. Please wait before posting again.")

        if response.status_code < 200 or response.status_code >= 300:
            raise PublishingError(f"Failed to publish tweet: {response.text}")

        return response.json()

    def _get_oauth1(self, encrypted_access_token: str) -> OAuth1:
        if not self.consumer_key or not self.consumer_secret:
            raise PublishingError("Twitter OAuth1 consumer credentials are not configured.")
        if not settings.TWITTER_ACCESS_TOKEN or not settings.TWITTER_ACCESS_TOKEN_SECRET:
            raise PublishingError("Twitter OAuth1 user access tokens are not configured.")
        consumer_key = self.consumer_key
        consumer_secret = self.consumer_secret
        owner_key = settings.TWITTER_ACCESS_TOKEN
        token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET
        return OAuth1(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=owner_key,
            resource_owner_secret=token_secret,
        )

    async def upload_media(
        self,
        encrypted_access_token: str,
        image_bytes: bytes,
        mime_type: str,
    ) -> str:
        """Upload image media to Twitter using simple upload."""
        oauth = self._get_oauth1(encrypted_access_token)
        url = "https://upload.twitter.com/1.1/media/upload.json"

        def _upload() -> requests.Response:
            files = {
                "media": ("upload", image_bytes, mime_type or "image/png"),
            }
            data = {
                "media_category": "tweet_image",
            }
            return requests.post(url=url, files=files, data=data, auth=oauth)

        response: requests.Response = await asyncio.to_thread(_upload)

        if response.status_code < 200 or response.status_code >= 300:
            raise PublishingError(f"Failed to upload media to Twitter: {response.text}")

        data = response.json()
        media_id = data.get("media_id_string") or data.get("media_id")
        if not media_id:
            raise PublishingError("Twitter media upload did not return a media ID.")

        return str(media_id)
    
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
