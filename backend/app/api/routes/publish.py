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

router = APIRouter()


class PublishRequest(BaseModel):
    """Request to publish content"""
    content: str
    image_url: Optional[str] = None


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
            encrypted_token = await user_connection_service.get_linkedin_access_token()
        except TokenExpiredError as exc:
            raise HTTPException(status_code=401, detail="LinkedIn token expired. Please reconnect your account.") from exc
        except PlatformConnectionError as exc:
            raise HTTPException(status_code=400, detail="LinkedIn account is not connected.") from exc

        result = await linkedin_service.publish_post(
            encrypted_access_token=encrypted_token,
            content=request.content,
            image_url=request.image_url
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
            encrypted_token = await user_connection_service.get_twitter_access_token()
        except TokenExpiredError as exc:
            raise HTTPException(status_code=401, detail="Twitter token expired. Please reconnect your account.") from exc
        except PlatformConnectionError as exc:
            raise HTTPException(status_code=400, detail="Twitter account is not connected.") from exc

        if request.mode == "thread" and request.thread_tweets:
            # Publish thread
            results = await twitter_service.publish_thread(
                encrypted_access_token=encrypted_token,
                tweets=request.thread_tweets
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
                encrypted_access_token=encrypted_token,
                content=request.content
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
        encrypted_token = await user_connection_service.get_linkedin_access_token()
        linkedin_result = await linkedin_service.publish_post(
            encrypted_access_token=encrypted_token,
            content=linkedin_request.content,
            image_url=linkedin_request.image_url
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
        encrypted_token = await user_connection_service.get_twitter_access_token()
        if twitter_request.mode == "thread" and twitter_request.thread_tweets:
            twitter_results = await twitter_service.publish_thread(
                encrypted_access_token=encrypted_token,
                tweets=twitter_request.thread_tweets
            )
            results["twitter"] = {
                "success": True,
                "mode": "thread",
                "tweet_ids": [r["data"]["id"] for r in twitter_results]
            }
        else:
            twitter_result = await twitter_service.publish_tweet(
                encrypted_access_token=encrypted_token,
                content=twitter_request.content
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
