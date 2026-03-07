from typing import Protocol


class LLMClient(Protocol):
    """Protocol for LLM clients that can categorize transcripts."""

    def categorize(self, transcript: str, categories: list[str]) -> dict[str, str]:
        """Categorize transcript and return category and summary.

        Args:
            transcript: The transcribed voice note text
            categories: List of valid category names

        Returns:
            Dict with 'category' and 'summary' keys
        """
        ...
