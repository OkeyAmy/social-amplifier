"""
Content generation routes
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.content import (
    GenerateLinkedInRequest,
    GenerateTwitterRequest,
    GeneratedContent,
    RefineRequest,
    TwitterTweet
)
from app.services.gemini import gemini_service
from app.core.exceptions import ContentGenerationError

router = APIRouter()


@router.post("/linkedin", response_model=GeneratedContent)
async def generate_linkedin_content(request: GenerateLinkedInRequest):
    """
    Generate LinkedIn-optimized content
    """
    try:
        # Analyze the idea first
        analysis = await gemini_service.analyze_idea(request.idea, request.emoji)
        
        # Generate LinkedIn content
        result = await gemini_service.generate_linkedin_content(
            idea=request.idea,
            emoji=request.emoji,
            mode=request.mode or "standard",
            tone=analysis.get("tone")
        )
        
        return GeneratedContent(
            original_idea=request.idea,
            emoji=request.emoji,
            platform="linkedin",
            mode=request.mode or "standard",
            generated_content=result["content"],
            character_count=result["character_count"],
            estimated_engagement="high" if result.get("professional_score", 0) > 75 else "medium",
            hashtags=result.get("hashtags", []),
            mentions=[],
            tone=result.get("tone"),
            professional_score=result.get("professional_score")
        )
    
    except ContentGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/twitter", response_model=GeneratedContent)
async def generate_twitter_content(request: GenerateTwitterRequest):
    """
    Generate Twitter/X-optimized content (single post or thread)
    """
    try:
        # Analyze the idea first
        analysis = await gemini_service.analyze_idea(request.idea, request.emoji)
        
        # Generate Twitter content
        result = await gemini_service.generate_twitter_content(
            idea=request.idea,
            emoji=request.emoji,
            mode=request.mode or "single",
            tone=analysis.get("tone")
        )
        
        # Prepare response
        response_data = {
            "original_idea": request.idea,
            "emoji": request.emoji,
            "platform": "twitter",
            "mode": request.mode or "single",
            "generated_content": result.get("content", ""),
            "character_count": result.get("character_count", 0),
            "estimated_engagement": "high" if len(request.idea) > 100 else "medium",
            "hashtags": result.get("hashtags", []),
            "mentions": [],
            "is_thread": result.get("is_thread", False)
        }
        
        # Add thread tweets if it's a thread
        if result.get("is_thread") and "tweets" in result:
            response_data["thread_tweets"] = [
                TwitterTweet(
                    sequence=tweet["sequence"],
                    content=tweet["content"],
                    character_count=tweet["character_count"]
                )
                for tweet in result["tweets"]
            ]
        else:
            response_data["character_count"] = result.get("character_count", len(result.get("content", "")))
        
        return GeneratedContent(**response_data)
    
    except ContentGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/refine")
async def refine_content(request: RefineRequest):
    """
    Refine existing content based on user instructions
    """
    try:
        result = await gemini_service.refine_content(
            current_content=request.content,
            instruction=request.instruction,
            platform=request.platform
        )
        
        return {
            "refined_content": result["refined_content"],
            "changes_made": result.get("changes_made", "Content refined based on your instruction"),
            "character_count": len(result["refined_content"])
        }
    
    except ContentGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.post("/analyze")
async def analyze_idea(idea: str, emoji: str = None):
    """
    Analyze user's idea and provide recommendations
    """
    try:
        analysis = await gemini_service.analyze_idea(idea, emoji)
        return analysis
    
    except ContentGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
