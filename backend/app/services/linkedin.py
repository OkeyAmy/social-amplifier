"""
LinkedIn API integration service
"""
import httpx
from typing import Optional, Dict
from datetime import datetime, timedelta

from urllib.parse import urlencode, quote

from app.core.config import settings
from app.core.security import encrypt_token, decrypt_token
from app.core.exceptions import PlatformConnectionError, TokenExpiredError, PublishingError


class LinkedInService:
    """Service for LinkedIn API interactions"""
    
    def __init__(self):
        self.client_id = settings.LINKEDIN_CLIENT_ID
        self.client_secret = settings.LINKEDIN_CLIENT_SECRET
        self.redirect_uri = settings.LINKEDIN_REDIRECT_URI
        self.auth_url = settings.LINKEDIN_AUTH_URL
        self.token_url = settings.LINKEDIN_TOKEN_URL
        self.api_url = settings.LINKEDIN_API_URL
    
    def get_authorization_url(self, state: str, redirect_uri: Optional[str] = None) -> str:
        """
        Generate LinkedIn OAuth authorization URL
        """
        scopes = ["r_liteprofile", "r_emailaddress", "w_member_social"]
        scope_string = " ".join(scopes)
        redirect = (redirect_uri or self.redirect_uri or "").strip()

        if not redirect:
            raise PlatformConnectionError("LinkedIn redirect URI is not configured.")
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect,
            "state": state,
            "scope": scope_string
        }

        query_string = urlencode(params, quote_via=quote)
        return f"{self.auth_url}?{query_string}"
    
    async def exchange_code_for_token(self, code: str, redirect_uri: Optional[str] = None) -> Dict:
        """
        Exchange authorization code for access token
        """
        redirect = (redirect_uri or self.redirect_uri or "").strip()

        if not redirect:
            raise PlatformConnectionError("LinkedIn redirect URI is not configured.")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    raise PlatformConnectionError(f"LinkedIn OAuth failed: {response.text}")
                
                data = response.json()
                
                # Encrypt tokens before storing
                return {
                    "access_token": encrypt_token(data["access_token"]),
                    "expires_in": data.get("expires_in", 5184000),  # Default 60 days
                    "refresh_token": encrypt_token(data.get("refresh_token", "")) if data.get("refresh_token") else None
                }
            
            except httpx.HTTPError as e:
                raise PlatformConnectionError(f"Failed to connect to LinkedIn: {str(e)}")
    
    async def get_user_profile(self, encrypted_access_token: str) -> Dict:
        """
        Retrieve user's LinkedIn profile
        """
        access_token = decrypt_token(encrypted_access_token)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.api_url}/me",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code == 401:
                    raise TokenExpiredError("LinkedIn access token expired")
                
                if response.status_code != 200:
                    raise PlatformConnectionError(f"Failed to fetch profile: {response.text}")
                
                return response.json()
            
            except httpx.HTTPError as e:
                raise PlatformConnectionError(f"Failed to fetch LinkedIn profile: {str(e)}")
    
    async def publish_post(
        self,
        encrypted_access_token: str,
        content: str,
        image_bytes: Optional[bytes] = None,
        image_mime_type: Optional[str] = None,
        owner_urn: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Publish a post to LinkedIn
        """
        access_token = decrypt_token(encrypted_access_token)
        
        # Get user's LinkedIn URN if not provided
        if not user_id:
            profile = await self.get_user_profile(encrypted_access_token)
            user_id = profile.get("id")

        author_urn = owner_urn or (f"urn:li:person:{user_id}" if user_id else None)

        if not author_urn:
            raise PublishingError("Unable to resolve LinkedIn member identifier for publishing.")

        asset_urn: Optional[str] = None
        if image_bytes:
            image_type = image_mime_type or "image/jpeg"
            asset_urn = await self.upload_image(
                encrypted_access_token,
                author_urn,
                image_bytes,
                image_type,
            )
        
        # Construct post payload
        post_data = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "IMAGE" if asset_urn else "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        # Add image if provided
        if asset_urn:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {
                    "status": "READY",
                    "description": {
                        "text": "Shared image"
                    },
                    "media": asset_urn,
                    "title": {
                        "text": "Image"
                    }
                }
            ]
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_url}/ugcPosts",
                    json=post_data,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                        "X-Restli-Protocol-Version": "2.0.0"
                    }
                )
                
                if response.status_code == 401:
                    raise TokenExpiredError("LinkedIn access token expired")
                
                if response.status_code not in [200, 201]:
                    raise PublishingError(f"Failed to publish to LinkedIn: {response.text}")
                
                return response.json()
            
            except httpx.HTTPError as e:
                raise PublishingError(f"Failed to publish to LinkedIn: {str(e)}")

    async def upload_image(
        self,
        encrypted_access_token: str,
        owner_urn: str,
        image_bytes: bytes,
        mime_type: str,
    ) -> str:
        """Register and upload an image to LinkedIn, returning the asset URN."""
        access_token = decrypt_token(encrypted_access_token)

        register_payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": owner_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }

        async with httpx.AsyncClient() as client:
            register_response = await client.post(
                "https://api.linkedin.com/v2/assets?action=registerUpload",
                json=register_payload,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )

            if register_response.status_code not in (200, 201):
                raise PublishingError(f"Failed to register LinkedIn image upload: {register_response.text}")

            data = register_response.json().get("value", {})
            upload_mechanism = data.get("uploadMechanism", {})
            upload_info = upload_mechanism.get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {})
            upload_url = upload_info.get("uploadUrl")
            asset = data.get("asset")

            if not upload_url or not asset:
                raise PublishingError("LinkedIn upload response missing asset information.")

            upload_headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": mime_type,
            }

            upload_response = await client.put(
                upload_url,
                content=image_bytes,
                headers=upload_headers,
            )

            if upload_response.status_code not in (200, 201):
                raise PublishingError(f"Failed to upload image to LinkedIn: {upload_response.text}")

            return asset
    
    async def refresh_access_token(self, encrypted_refresh_token: str) -> Dict:
        """
        Refresh LinkedIn access token
        """
        refresh_token = decrypt_token(encrypted_refresh_token)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_url,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                
                if response.status_code != 200:
                    raise TokenExpiredError("Failed to refresh LinkedIn token")
                
                data = response.json()
                
                return {
                    "access_token": encrypt_token(data["access_token"]),
                    "expires_in": data.get("expires_in", 5184000)
                }
            
            except httpx.HTTPError as e:
                raise TokenExpiredError(f"Failed to refresh token: {str(e)}")


# Singleton instance
linkedin_service = LinkedInService()
