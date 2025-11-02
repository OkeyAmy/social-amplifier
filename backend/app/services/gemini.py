"""
Google Gemini AI service for content generation
"""
import google.generativeai as genai
from typing import Optional, List
import json
import re

from app.core.config import settings
from app.core.exceptions import ContentGenerationError


class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini service"""
        if not settings.GEMINI_API_KEY:
            raise ContentGenerationError("Gemini API key not configured")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def analyze_idea(self, idea: str, emoji: Optional[str] = None) -> dict:
        """
        Analyze the user's idea to determine tone, sentiment, and recommendations
        """
        prompt = f"""
        Analyze this user idea and provide a JSON response:
        
        Idea: "{idea}"
        Selected Emoji: {emoji if emoji else "None"}
        
        Return a JSON object with:
        - tone: (casual, professional, excited, reflective, frustrated, celebratory)
        - sentiment: (positive, negative, neutral)
        - complexity: (simple, moderate, complex)
        - recommended_platform: (linkedin, twitter, both)
        - recommended_mode: (for Twitter: single or thread; for LinkedIn: standard, article, or quick)
        - confidence: (0.0 to 1.0)
        - key_themes: (list of 2-3 main themes)
        
        Respond ONLY with valid JSON, no additional text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            return result
        except Exception as e:
            raise ContentGenerationError(f"Failed to analyze idea: {str(e)}")
    
    async def generate_linkedin_content(
        self,
        idea: str,
        emoji: Optional[str] = None,
        mode: str = "standard",
        tone: Optional[str] = None
    ) -> dict:
        """
        Generate LinkedIn-optimized content
        """
        mode_instructions = {
            "standard": "1,200-1,500 characters, professional expansion with storytelling",
            "article": "2,000-3,000 characters, thought leadership style, in-depth analysis",
            "quick": "300-500 characters, brief professional update, punchy and direct"
        }
        
        instruction = mode_instructions.get(mode, mode_instructions["standard"])
        
        prompt = f"""
        Transform this idea into LinkedIn-optimized content:
        
        Original Idea: "{idea}"
        Selected Emoji: {emoji if emoji else "None"}
        Mode: {mode} ({instruction})
        Tone: {tone if tone else "Infer from the idea"}
        
        CRITICAL RULES:
        1. Preserve the core message and intent - DO NOT change the fundamental idea
        2. Maintain the user's authentic voice while enhancing clarity
        3. Keep personal anecdotes and specific details intact
        
        Create professional LinkedIn content with:
        - Hook opening line (attention-grabbing)
        - Well-structured body with line breaks for readability
        - Strategic emoji placement (professional, 2-3 maximum)
        - 3-5 relevant industry hashtags
        - Call-to-action or thought-provoking conclusion
        
        Return JSON:
        {{
            "content": "the generated post",
            "hashtags": ["hashtag1", "hashtag2"],
            "tone": "detected/applied tone",
            "professional_score": 85,
            "character_count": 1234
        }}
        
        Respond ONLY with valid JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            return result
        except Exception as e:
            raise ContentGenerationError(f"Failed to generate LinkedIn content: {str(e)}")
    
    async def generate_twitter_content(
        self,
        idea: str,
        emoji: Optional[str] = None,
        mode: str = "single",
        tone: Optional[str] = None
    ) -> dict:
        """
        Generate Twitter/X-optimized content (single post or thread)
        """
        if mode == "single":
            return await self._generate_single_tweet(idea, emoji, tone)
        else:
            return await self._generate_thread(idea, emoji, tone)
    
    async def _generate_single_tweet(
        self,
        idea: str,
        emoji: Optional[str],
        tone: Optional[str]
    ) -> dict:
        """Generate a single tweet"""
        prompt = f"""
        Transform this idea into a concise, punchy tweet:
        
        Original Idea: "{idea}"
        Selected Emoji: {emoji if emoji else "None"}
        Tone: {tone if tone else "Infer from the idea"}
        
        CRITICAL RULES:
        1. Preserve the core message - DO NOT change the fundamental idea
        2. Keep the user's authentic voice
        3. Maximum 270 characters (leave room for potential edits)
        
        Create engaging tweet content with:
        - Front-loaded key message
        - Incorporate emoji naturally
        - 1-3 relevant trending hashtags
        - Creates curiosity or urgency when appropriate
        
        Return JSON:
        {{
            "content": "the tweet text",
            "hashtags": ["hashtag1", "hashtag2"],
            "character_count": 245
        }}
        
        Respond ONLY with valid JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            result["is_thread"] = False
            return result
        except Exception as e:
            raise ContentGenerationError(f"Failed to generate tweet: {str(e)}")
    
    async def _generate_thread(
        self,
        idea: str,
        emoji: Optional[str],
        tone: Optional[str]
    ) -> dict:
        """Generate a Twitter thread"""
        prompt = f"""
        Transform this idea into a compelling Twitter thread (3-10 tweets):
        
        Original Idea: "{idea}"
        Selected Emoji: {emoji if emoji else "None"}
        Tone: {tone if tone else "Infer from the idea"}
        
        CRITICAL RULES:
        1. Preserve the core message and narrative - DO NOT deviate
        2. Maintain the user's authentic voice throughout
        3. Each tweet must stand alone but flow cohesively
        
        Create thread with:
        - First tweet: Compelling hook with thread indicator (1/X)
        - Middle tweets: Develop idea with examples, data, or narrative
        - Final tweet: Conclusion with CTA + "End of thread" indicator
        - Strategic emoji use (1-2 per tweet maximum)
        - Each tweet under 270 characters
        
        Return JSON:
        {{
            "tweets": [
                {{"sequence": 1, "content": "First tweet...", "character_count": 245}},
                {{"sequence": 2, "content": "Second tweet...", "character_count": 268}}
            ],
            "thread_summary": "Brief summary of the thread",
            "total_tweets": 5,
            "hashtags": ["hashtag1", "hashtag2"]
        }}
        
        Respond ONLY with valid JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            result["is_thread"] = True
            
            # Combine tweets into single content for preview
            tweets_text = "\n\n---\n\n".join([t["content"] for t in result["tweets"]])
            result["content"] = tweets_text
            
            return result
        except Exception as e:
            raise ContentGenerationError(f"Failed to generate thread: {str(e)}")
    
    async def refine_content(
        self,
        current_content: str,
        instruction: str,
        platform: str
    ) -> dict:
        """
        Refine existing content based on user instructions
        """
        prompt = f"""
        Refine this {platform} content based on the user's instruction:
        
        Current Content:
        "{current_content}"
        
        User Instruction: "{instruction}"
        
        Refine the content while:
        - Following the user's specific instruction
        - Maintaining the core message
        - Keeping it optimized for {platform}
        - Preserving character limits
        
        Return JSON:
        {{
            "refined_content": "the improved content",
            "changes_made": "brief description of changes"
        }}
        
        Respond ONLY with valid JSON.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            return result
        except Exception as e:
            raise ContentGenerationError(f"Failed to refine content: {str(e)}")
    
    def _parse_json_response(self, text: str) -> dict:
        """Parse JSON from AI response, handling markdown code blocks"""
        # Remove markdown code blocks if present
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ContentGenerationError(f"Failed to parse AI response as JSON: {str(e)}")


# Singleton instance
gemini_service = GeminiService()
