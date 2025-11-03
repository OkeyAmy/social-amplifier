"""
Publishing routes for LinkedIn and Twitter
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel

from app.services.linkedin import linkedin_service
from app.services.twitter import twitter_service
from app.services.user_connections import user_connection_service
from app.core.exceptions import PublishingError, TokenExpiredError, RateLimitError, PlatformConnectionError
from base64 import b64decode
import binascii


MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB


def _parse_base64_image(data: Optional[str]) -> Optional[bytes]:
    if not data:
        return None

    try:
        decoded = b64decode(data)
        if len(decoded) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=400, detail="Image exceeds 10MB limit.")
        return decoded
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Invalid image payload.") from exc

router = APIRouter()


class PublishRequest(BaseModel):
    """Request to publish content"""
    content: str
    image_base64: Optional[str] = None
    image_mime_type: Optional[str] = None


class PublishTwitterRequest(PublishRequest):
    """Request to publish to Twitter"""
    mode: str = "single"  # "single" or "thread"
    thread_tweets: Optional[List[str]] = None  # For thread mode


@router.post("/linkedin")
async def publish_to_linkedin(request: PublishRequest):
    """
    Publish content to LinkedIn
    """
    try:
        try:
            connection = await user_connection_service.get_linkedin_connection()
        except TokenExpiredError as exc:
            raise HTTPException(status_code=401, detail="LinkedIn token expired. Please reconnect your account.") from exc
        except PlatformConnectionError as exc:
            raise HTTPException(status_code=400, detail="LinkedIn account is not connected.") from exc

        image_bytes = _parse_base64_image(request.image_base64)
        owner_urn = f"urn:li:person:{connection.user_id}" if connection.user_id else None
        result = await linkedin_service.publish_post(
            encrypted_access_token=connection.access_token,
            content=request.content,
            image_bytes=image_bytes,
            image_mime_type=request.image_mime_type,
            owner_urn=owner_urn,
        )
        
        return {
            "success": True,
            "platform": "linkedin",
            "post_id": result.get("id"),
            "message": "Successfully published to LinkedIn"
        }
    
    except TokenExpiredError as e:
        raise HTTPException(status_code=401, detail="LinkedIn token expired. Please reconnect your account.")
    except PublishingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/twitter")
async def publish_to_twitter(request: PublishTwitterRequest):
    """
    Publish content to Twitter (single post or thread)
    """
    try:
        try:
            connection = await user_connection_service.get_twitter_connection()
        except TokenExpiredError as exc:
            raise HTTPException(status_code=401, detail="Twitter token expired. Please reconnect your account.") from exc
        except PlatformConnectionError as exc:
            raise HTTPException(status_code=400, detail="Twitter account is not connected.") from exc

        media_ids: Optional[List[str]] = None
        image_bytes = _parse_base64_image(request.image_base64)
        if image_bytes:
            media_id = await twitter_service.upload_media(
                encrypted_access_token=connection.access_token,
                image_bytes=image_bytes,
                mime_type=request.image_mime_type or "image/jpeg",
            )
            media_ids = [media_id]

        if request.mode == "thread" and request.thread_tweets:
            # Publish thread
            results = await twitter_service.publish_thread(
                encrypted_access_token=connection.access_token,
                tweets=request.thread_tweets,
                image_ids=media_ids,
            )
            
            return {
                "success": True,
                "platform": "twitter",
                "mode": "thread",
                "tweet_ids": [r["data"]["id"] for r in results],
                "tweet_count": len(results),
                "message": f"Successfully published thread with {len(results)} tweets"
            }
        else:
            # Publish single tweet
            result = await twitter_service.publish_tweet(
                encrypted_access_token=connection.access_token,
                content=request.content,
                image_ids=media_ids,
            )
            
            return {
                "success": True,
                "platform": "twitter",
                "mode": "single",
                "tweet_id": result["data"]["id"],
                "message": "Successfully published to Twitter"
            }
    
    except TokenExpiredError as e:
        raise HTTPException(status_code=401, detail="Twitter token expired. Please reconnect your account.")
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except PublishingError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/both")
async def publish_to_both_platforms(
    linkedin_request: PublishRequest,
    twitter_request: PublishTwitterRequest
):
    """
    Publish to both LinkedIn and Twitter
    """
    results = {
        "linkedin": {"success": False},
        "twitter": {"success": False}
    }
    errors = []
    
    # Publish to LinkedIn
    try:
        connection = await user_connection_service.get_linkedin_connection()
        owner_urn = f"urn:li:person:{connection.user_id}" if connection.user_id else None
        image_bytes = _parse_base64_image(linkedin_request.image_base64)

        linkedin_result = await linkedin_service.publish_post(
            encrypted_access_token=connection.access_token,
            content=linkedin_request.content,
            image_bytes=image_bytes,
            image_mime_type=linkedin_request.image_mime_type,
            owner_urn=owner_urn,
        )
        results["linkedin"] = {
            "success": True,
            "post_id": linkedin_result.get("id")
        }
    except (PlatformConnectionError, TokenExpiredError) as exc:
        errors.append(f"LinkedIn: {str(exc)}")
    except Exception as e:
        errors.append(f"LinkedIn: {str(e)}")
    
    # Publish to Twitter
    try:
        connection = await user_connection_service.get_twitter_connection()
        media_ids: Optional[List[str]] = None
        image_bytes = _parse_base64_image(twitter_request.image_base64)
        if image_bytes:
            media_id = await twitter_service.upload_media(
                encrypted_access_token=connection.access_token,
                image_bytes=image_bytes,
                mime_type=twitter_request.image_mime_type or "image/jpeg",
            )
            media_ids = [media_id]

        if twitter_request.mode == "thread" and twitter_request.thread_tweets:
            twitter_results = await twitter_service.publish_thread(
                encrypted_access_token=connection.access_token,
                tweets=twitter_request.thread_tweets,
                image_ids=media_ids,
            )
            results["twitter"] = {
                "success": True,
                "mode": "thread",
                "tweet_ids": [r["data"]["id"] for r in twitter_results]
            }
        else:
            twitter_result = await twitter_service.publish_tweet(
                encrypted_access_token=connection.access_token,
                content=twitter_request.content,
                image_ids=media_ids,
            )
            results["twitter"] = {
                "success": True,
                "mode": "single",
                "tweet_id": twitter_result["data"]["id"]
            }
    except (PlatformConnectionError, TokenExpiredError) as exc:
        errors.append(f"Twitter: {str(exc)}")
    except Exception as e:
        errors.append(f"Twitter: {str(e)}")
    
    success_count = sum(1 for r in results.values() if r["success"])
    
    return {
        "results": results,
        "success_count": success_count,
        "total": 2,
        "errors": errors if errors else None,
        "message": f"Published to {success_count} out of 2 platforms"
    }
