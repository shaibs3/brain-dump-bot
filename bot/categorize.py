from bot.llm import LLMClient, get_llm_client
from config import CATEGORIES

_client: LLMClient | None = None


def _get_client() -> LLMClient:
    """Get or create LLM client."""
    global _client
    if _client is None:
        _client = get_llm_client()
    return _client


def categorize_note(transcript: str) -> dict[str, str]:
    """Categorize transcript and generate summary using configured LLM.

    Args:
        transcript: The transcribed voice note text

    Returns:
        Dict with 'category' and 'summary' keys
    """
    client = _get_client()
    return client.categorize(transcript, list(CATEGORIES))
