from google import genai

from bot.llm.prompt import build_full_prompt, parse_response, validate_category


class GeminiClient:
    """Google Gemini LLM client for categorization."""

    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(self, api_key: str, model: str | None = None):
        """Initialize Gemini client.

        Args:
            api_key: Google Gemini API key
            model: Model to use (defaults to gemini-2.0-flash)
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
        prompt = build_full_prompt(categories, transcript)
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        content = response.text if response.text else None
        result = parse_response(content, transcript)
        result["category"] = validate_category(result["category"], categories)
        return result
