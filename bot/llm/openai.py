import logging

from openai import APIConnectionError, AuthenticationError, OpenAI, RateLimitError

from bot.llm.prompt import build_system_prompt, parse_response, validate_category

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI LLM client for categorization."""

    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, api_key: str, model: str | None = None):
        """Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            model: Model to use (defaults to gpt-4o-mini)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model or self.DEFAULT_MODEL

    def categorize(self, transcript: str, categories: list[str]) -> dict[str, str]:
        """Categorize transcript using OpenAI.

        Args:
            transcript: The transcribed voice note text
            categories: List of valid category names

        Returns:
            Dict with 'category' and 'summary' keys
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": build_system_prompt(categories)},
                    {"role": "user", "content": transcript},
                ],
                temperature=0.3,
                max_tokens=150,
            )

            content = response.choices[0].message.content
            result = parse_response(content, transcript)
            result["category"] = validate_category(result["category"], categories)
            return result

        except AuthenticationError:
            logger.error("OpenAI authentication failed. Check your API key.")
            return _fallback_response(transcript)
        except RateLimitError:
            logger.warning("OpenAI rate limit exceeded. Using fallback.")
            return _fallback_response(transcript)
        except APIConnectionError:
            logger.error("Failed to connect to OpenAI API.")
            return _fallback_response(transcript)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return _fallback_response(transcript)


def _fallback_response(transcript: str) -> dict[str, str]:
    """Generate fallback response when API fails."""
    return {
        "category": "Projects",
        "summary": transcript[:100] if len(transcript) > 100 else transcript,
    }
