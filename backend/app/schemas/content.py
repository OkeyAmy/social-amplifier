"""
Pydantic schemas for content-related requests and responses
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Request to generate content"""
    idea: str = Field(..., min_length=10, max_length=5000, description="User's original idea")
    emoji: Optional[str] = Field(None, max_length=10, description="Selected emoji")
    mode: Optional[str] = Field(None, description="Content mode (for Twitter: 'single' or 'thread')")
    user_id: Optional[int] = Field(None, description="User ID for personalization")


class GenerateLinkedInRequest(GenerateRequest):
    """Request to generate LinkedIn content"""
    mode: Optional[str] = Field("standard", description="LinkedIn mode: 'standard', 'article', or 'quick'")


class GenerateTwitterRequest(GenerateRequest):
    """Request to generate Twitter content"""
    mode: Optional[str] = Field("single", description="Twitter mode: 'single' or 'thread'")


class TwitterTweet(BaseModel):
    """Single tweet in a thread"""
    sequence: int
    content: str
    character_count: int


class GeneratedContent(BaseModel):
    """Generated content response"""
    original_idea: str
    emoji: Optional[str]
    platform: str
    mode: Optional[str]
    generated_content: str
    character_count: int
    estimated_engagement: str
    hashtags: List[str] = []
    mentions: List[str] = []
    
    # Twitter-specific
    is_thread: bool = False
    thread_tweets: List[TwitterTweet] = []
    
    # LinkedIn-specific
    tone: Optional[str] = None
    professional_score: Optional[int] = None


class RefineRequest(BaseModel):
    """Request to refine existing content"""
    content: str = Field(..., min_length=10, description="Current content")
    instruction: str = Field(..., min_length=5, max_length=500, description="Refinement instruction")
    platform: str = Field(..., description="Target platform")


class ContentAnalysis(BaseModel):
    """Content analysis from AI"""
    tone: str
    sentiment: str
    complexity: str
    recommended_platform: str
    recommended_mode: str
    confidence: float
