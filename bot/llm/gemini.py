import logging

from google import genai
from google.genai import errors as genai_errors

from bot.llm.prompt import build_full_prompt, parse_response, validate_category

logger = logging.getLogger(__name__)


class GeminiClient:
    """Google Gemini LLM client for categorization."""

    DEFAULT_MODEL = "gemini-3-flash-preview"

    def __init__(self, api_key: str, model: str | None = None):
        """Initialize Gemini client.

        Args:
            api_key: Google Gemini API key
            model: Model to use (defaults to gemini-3-flash-preview)
        """
        self.client = genai.Client(api_key=api_key)
        self.model = model or self.DEFAULT_MODEL

    def categorize(self, transcript: str, categories: list[str]) -> dict[str, str]:
        """Categorize transcript using Gemini.

        Args:
            transcript: The transcribed voice note text
            categories: List of valid category names

        Returns:
            Dict with 'category' and 'summary' keys
        """
        try:
            prompt = build_full_prompt(categories, transcript)
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )

            content = response.text if response.text else None
            result = parse_response(content, transcript)
            result["category"] = validate_category(result["category"], categories)
            return result

        except genai_errors.ClientError as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                logger.warning("Gemini rate limit exceeded. Using fallback.")
            elif "401" in str(e) or "403" in str(e):
                logger.error("Gemini authentication failed. Check your API key.")
            else:
                logger.error(f"Gemini client error: {e}")
            return _fallback_response(transcript)
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return _fallback_response(transcript)


def _fallback_response(transcript: str) -> dict[str, str]:
    """Generate fallback response when API fails."""
    return {
        "category": "Projects",
        "summary": transcript[:100] if len(transcript) > 100 else transcript,
    }
