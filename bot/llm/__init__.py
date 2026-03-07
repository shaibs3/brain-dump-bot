from bot.llm.base import LLMClient

# Lazy imports to avoid loading unused SDKs
_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client based on configuration.

    Returns:
        LLM client instance (OpenAI or Gemini based on LLM_PROVIDER)

    Raises:
        ValueError: If provider is unknown or API key is missing
    """
    global _client
    if _client is not None:
        return _client

    from config import GEMINI_API_KEY, LLM_MODEL, LLM_PROVIDER, OPENAI_API_KEY

    if LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
        from bot.llm.gemini import GeminiClient

        _client = GeminiClient(GEMINI_API_KEY, LLM_MODEL)
    elif LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        from bot.llm.openai import OpenAIClient

        _client = OpenAIClient(OPENAI_API_KEY, LLM_MODEL)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")

    return _client


def reset_client() -> None:
    """Reset the cached client. Useful for testing."""
    global _client
    _client = None


__all__ = ["LLMClient", "get_llm_client", "reset_client"]
