"""
Google Gemini AI service for content generation
"""
import google.generativeai as genai
from typing import Optional
import json
import re

from app.core.config import settings
from app.core.exceptions import ContentGenerationError


SYSTEM_PROMPT = """
You are POSTBLASTER - the senior social strategist who turns raw ideas into platform-native posts.

MISSION
- Preserve the user's truth, point of view, and topic.
- Make every generated post immediately publishable.
- Use the platform-specific style contract in the user prompt as the source of truth.

NON-NEGOTIABLES
1. Output compact JSON only. No prose, Markdown, code fences, or labels outside the requested schema.
2. Never invent stats, quotes, credentials, results, or names that the user did not provide.
3. Respect hard limits. LinkedIn posts must stay <= 3000 characters. X posts must stay <= 280 characters.
4. Avoid corporate filler: "excited to share", "thrilled", "humbled", "leverage", "synergy", "unlock", "thought leadership", "circle back".
5. Emoji usage is platform-specific. If a selected emoji is provided, reflect it exactly as directed by the platform prompt.
6. Use hashtags only when the platform prompt asks for them. Never spam.
7. Keep formatting clean, readable, and copy-paste ready.
"""

LINKEDIN_POST_PROMPT = """
LINKEDIN STYLE CONTRACT
- Write like a sharp founder/operator post, not a press release.
- Hook must stop the scroll in line 1. No "excited to share" openings.
- Body should use short paragraphs separated by double line breaks.
- Use a clear rhythm: hook -> context -> lesson/insight -> practical takeaway -> soft CTA.
- Keep the voice direct, human, and slightly punchy. Professional does not mean bland.
- Avoid corporate buzzwords and empty motivation.
- If selected_emoji is provided, use it 1-3 times total:
  - once in the hook or first transition,
  - optionally once as a visual bullet/marker,
  - optionally once near the CTA.
- Do not use random emojis. Only use selected_emoji.
- Hashtags: return 3-5 relevant hashtags in the hashtags array. Do not force them into content unless it reads naturally.
"""

PRIMEGEN_TWEET_PROMPT = """
PRIMEGEN X POST STYLE CONTRACT

Write X posts with the high-energy programmer cadence of a Primeagen-like engineering shitpost:
short, punchy, anti-corporate, skeptical of hype, funny because it is partly true.

HARD LIMIT
- Every single X post must be <= 280 characters.
- Aim for 180-240 characters.
- Count before returning. If it is too long, rewrite. Do not truncate with "...".

VOICE
- Short declarative fragments.
- It should sound typed in the moment, not polished by marketing.
- Prefer conviction over hedging.
- Use period-weighted fragments: "Skill issue."
- Use "lmao" only when the post is roast/chaos, not sincere.
- Use ALL CAPS sparingly on one key word for emphasis.
- Never sound like LinkedIn.

GOOD WORDS WHEN NATURAL
lmao, bro, actually, literally, genuinely, insane, terrible, amazing, skill issue,
the worst, real talk, please, no way, wait, I can't, that's it, touch grass,
just, cope, grind, I'm not gonna lie, have you tried

NEVER USE
utilize, leverage, synergy, paradigm shift, deep dive, unpack, stakeholder,
bandwidth, circle back, thought leadership, empower, democratize, unlock

TOPIC FINGERPRINTS
- Neovim/Vim: conviction, Vim motions, editor-as-discipline.
- Rust: borrow checker humility, correctness, speed, growth.
- JavaScript/TypeScript/React/npm: useful chaos, framework churn, node_modules jokes.
- Career/learning: fundamentals, shipping, skill gaps, learning by building.
- AI/LLMs: useful assistant, confidently wrong, distrust marketing hype.
- Engineering: simple > complex, abstractions must earn existence, profile before guessing.

STRUCTURES
A. Hot take drop: claim -> reason -> kicker.
B. Callback roast: seeming agreement -> flip -> sting.
C. Observation + exhale: industry behavior -> implication -> weighted ending.
D. Sincere one: real talk -> honest point -> landing line.
E. Running bit: recurring joke -> today's variant -> absurd confirmation.
F. Mid-thought start: starts like the reader walked into a rant.
G. Rhetorical setup: Nobody: -> group says the ridiculous thing.
H. Concession + pivot: "X is fine. But..."

EMOJI RULE
- If selected_emoji is provided, use it exactly once when it fits the post.
- It should feel like punctuation, not decoration.
- If no selected_emoji is provided, use no emoji.

FORMAT RULES
- Return JSON only using the requested schema.
- Do not include TWEET:, CHAR COUNT:, template labels, notes, or explanations in the content field.
- For hashtags, return [] unless the user explicitly asked for hashtags.
- Make sure you do not deviate from the context of the writing of the user
"""

TWITTER_MAX_CHARS = 280


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
        
        selected_emoji = emoji or "none"

        prompt = f"""
        Craft LinkedIn content from this idea.

        original_idea: "{idea}"
        selected_emoji: "{selected_emoji}"
        selected_mode: "{mode}" (guidance: {instruction})
        tone_override: "{tone if tone else 'infer'}"

        {LINKEDIN_POST_PROMPT}

        Required output:
        - Content length should follow selected_mode guidance and stay <=3000 characters.
        - If selected_emoji is not "none", the content field must include that exact emoji at least once.
        - Keep hashtags in the hashtags array. Do not append a hashtag wall to the content field.

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
            content = result.get("content", "")
            if emoji and emoji not in content:
                content = f"{emoji} {content}".strip()
                result["content"] = content
            result["character_count"] = len(content)
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
        selected_emoji = emoji or "none"

        prompt = f"""
        Convert the idea into a single X post.

        idea: "{idea}"
        selected_emoji: "{selected_emoji}"
        tone_override: "{tone if tone else 'infer'}"

        {PRIMEGEN_TWEET_PROMPT}

        Required output:
        - The content field must be <=280 characters.
        - If selected_emoji is not "none", include that exact emoji once if it fits.
        - No hashtags unless the original idea explicitly asks for hashtags.

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
            result = self._normalize_tweet_result(result, emoji)
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
        selected_emoji = emoji or "none"

        prompt = f"""
        Build a Twitter thread (3-10 tweets) from this idea.

        idea: "{idea}"
        selected_emoji: "{selected_emoji}"
        tone_override: "{tone if tone else 'infer'}"

        {PRIMEGEN_TWEET_PROMPT}

        Required output:
        - Each tweet content must be <=280 characters.
        - Use the same Prime-like cadence across the thread.
        - First tweet must hook hard with (1/N).
        - Final tweet should land with a sting, takeaway, or real-talk line. Do not use "End of thread".
        - If selected_emoji is not "none", include that exact emoji once in the whole thread if it fits.
        - No hashtags unless the original idea explicitly asks for hashtags.

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
            result = self._normalize_thread_result(result, emoji)
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

    def _normalize_tweet_result(self, result: dict, emoji: Optional[str]) -> dict:
        """Keep X output inside the hard character cap after model generation."""
        content = str(result.get("content", "")).strip()

        if emoji and emoji not in content and len(f"{content} {emoji}".strip()) <= TWITTER_MAX_CHARS:
            content = f"{content} {emoji}".strip()

        if len(content) > TWITTER_MAX_CHARS:
            content = self._trim_to_character_limit(content, TWITTER_MAX_CHARS)

        result["content"] = content
        result["character_count"] = len(content)
        result.setdefault("hashtags", [])
        return result

    def _normalize_thread_result(self, result: dict, emoji: Optional[str]) -> dict:
        """Normalize each thread tweet and keep selected emoji reflected once when possible."""
        tweets = result.get("tweets", [])
        normalized_tweets = []
        emoji_seen = False

        for tweet in tweets:
            content = str(tweet.get("content", "")).strip()
            if emoji and emoji in content:
                emoji_seen = True
            if len(content) > TWITTER_MAX_CHARS:
                content = self._trim_to_character_limit(content, TWITTER_MAX_CHARS)

            normalized_tweets.append({
                **tweet,
                "content": content,
                "character_count": len(content),
            })

        if emoji and not emoji_seen and normalized_tweets:
            first_content = normalized_tweets[0]["content"]
            with_emoji = f"{first_content} {emoji}".strip()
            if len(with_emoji) <= TWITTER_MAX_CHARS:
                normalized_tweets[0]["content"] = with_emoji
                normalized_tweets[0]["character_count"] = len(with_emoji)

        result["tweets"] = normalized_tweets
        result["total_tweets"] = len(normalized_tweets)
        result.setdefault("hashtags", [])
        return result

    def _trim_to_character_limit(self, content: str, limit: int) -> str:
        """Trim copy at a natural boundary without adding ellipses."""
        trimmed = content[:limit].rstrip()
        boundary = max(trimmed.rfind("."), trimmed.rfind("!"), trimmed.rfind("?"), trimmed.rfind("\n"))

        if boundary > 0 and boundary >= int(limit * 0.65):
            return trimmed[:boundary + 1].rstrip()

        word_boundary = trimmed.rfind(" ")
        if word_boundary > 0 and word_boundary >= int(limit * 0.65):
            return trimmed[:word_boundary].rstrip()

        return trimmed


# Singleton instance
gemini_service = GeminiService()
