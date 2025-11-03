"""
Google Gemini AI service for content generation
"""
import google.generativeai as genai
from typing import Optional, List
import json
import re

from app.core.config import settings
from app.core.exceptions import ContentGenerationError


SYSTEM_PROMPT = """
You are PostBlaster, a senior social content strategist helping busy founders ship platform-native posts.

Non-negotiables:
- Keep the creator's original facts, intentions, and voice intact?never invent data or names.
- Default to inclusive, encouraging language that sounds human and grounded.
- Deliver compact JSON only. No prose, Markdown, or code fences.
- Respect platform limits (LinkedIn ? 3000 chars; X tweets ? 270 chars) and make content skimmable.
- When structuring content, think in hooks, snackable sections, and clear calls-to-action.

If the idea lacks detail, sharpen the message without fabricating specifics.
"""


class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        """Initialize Gemini service"""
        if not settings.GEMINI_API_KEY:
            raise ContentGenerationError("Gemini API key not configured")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction=SYSTEM_PROMPT,
        )
    
    async def analyze_idea(self, idea: str, emoji: Optional[str] = None) -> dict:
        """
        Analyze the user's idea to determine tone, sentiment, and recommendations
        """
        prompt = f"""
        Evaluate the idea below and respond with JSON only.

        idea: "{idea}"
        emoji_hint: "{emoji if emoji else 'None'}"

        JSON schema:
        {{
          "tone": "casual|professional|excited|reflective|frustrated|celebratory",
          "sentiment": "positive|negative|neutral",
          "complexity": "simple|moderate|complex",
          "recommended_platform": "linkedin|twitter|both",
          "recommended_mode": "single|thread|standard|article|quick",
          "confidence": float (0.0 - 1.0),
          "key_themes": ["theme1", "theme2"]
        }}
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
        Craft LinkedIn content from this idea.

        original_idea: "{idea}"
        emoji_hint: "{emoji if emoji else 'None'}"
        selected_mode: "{mode}" (guidance: {instruction})
        tone_override: "{tone if tone else 'infer'}"

        Produce a hooky intro, short paragraphs, and a closing CTA or question.
        Use <=3 tasteful emojis and 3-5 relevant hashtags. Keep the voice authentic.

        Return JSON only:
        {{
          "content": "...",
          "hashtags": ["#tag"],
          "tone": "...",
          "professional_score": int (0-100),
          "character_count": int
        }}
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
        Convert the idea into a single X post (<=270 characters).

        idea: "{idea}"
        emoji_hint: "{emoji if emoji else 'None'}"
        tone_override: "{tone if tone else 'infer'}"

        Return JSON only:
        {{
          "content": "tweet text",
          "hashtags": ["#tag"],
          "character_count": int
        }}
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
        Build a Twitter thread (3-10 tweets) from this idea.

        idea: "{idea}"
        emoji_hint: "{emoji if emoji else 'None'}"
        tone_override: "{tone if tone else 'infer'}"

        Each tweet must be <=270 characters. The first tweet hooks with (1/N); the final tweet lands a CTA and "End of thread" signal. Maintain a consistent, authentic voice.

        Return JSON only:
        {{
          "tweets": [{{"sequence": 1, "content": "...", "character_count": int}}],
          "thread_summary": "...",
          "total_tweets": int,
          "hashtags": ["#tag"]
        }}
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
        Refine the {platform} post below according to the instruction. Maintain intent and platform constraints.

        content: "{current_content}"
        instruction: "{instruction}"

        Return JSON only:
        {{
          "refined_content": "...",
          "changes_made": "..."
        }}
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
