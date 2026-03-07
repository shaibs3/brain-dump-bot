def build_system_prompt(categories: list[str]) -> str:
    """Build the system prompt for categorization.

    Args:
        categories: List of valid category names

    Returns:
        System prompt string
    """
    return f"""You are a categorization assistant. Given a transcribed voice note, you must:
1. Categorize it into exactly one of these categories: {", ".join(categories)}
2. Write a concise one-line summary (max 100 characters)

Category guidelines:
- Career: Work, job, professional tasks, meetings, deadlines
- Health: Medical, doctor appointments, medications, mental health
- Fitness: Exercise, gym, workouts, sports, physical activity
- Relationships: Family, friends, social plans, personal connections
- Finance: Money, bills, investments, budgets, purchases
- Learning: Education, courses, books, skills, self-improvement
- Projects: Personal projects, hobbies, side tasks, anything else

Respond ONLY with valid JSON in this format:
{{"category": "CategoryName", "summary": "One line summary"}}

Rules:
- If the note doesn't clearly fit a category, use "Projects" as default
- The summary should be actionable when possible (start with verb)
- Keep the summary brief and clear
"""


def build_full_prompt(categories: list[str], transcript: str) -> str:
    """Build a full prompt combining system instructions and user input.

    Used for APIs that don't have separate system/user message roles.

    Args:
        categories: List of valid category names
        transcript: The transcribed voice note text

    Returns:
        Complete prompt string
    """
    system_prompt = build_system_prompt(categories)
    return f"{system_prompt}\n\nTranscript to categorize:\n{transcript}"


def parse_response(content: str | None, transcript: str) -> dict[str, str]:
    """Parse LLM response into category and summary.

    Args:
        content: Raw response content from LLM
        transcript: Original transcript (used for fallback)

    Returns:
        Dict with 'category' and 'summary' keys
    """
    import json

    if content is None:
        return _fallback_response(transcript)

    content = content.strip()

    try:
        result: dict[str, str] = json.loads(content)
        # Validate category exists
        if not result.get("category"):
            result["category"] = "Projects"
        # Ensure summary exists
        if not result.get("summary"):
            result["summary"] = _truncate(transcript)
        return result
    except json.JSONDecodeError:
        return _fallback_response(transcript)


def validate_category(category: str, valid_categories: list[str]) -> str:
    """Validate and normalize category.

    Args:
        category: Category from LLM response
        valid_categories: List of valid category names

    Returns:
        Valid category name (falls back to "Projects")
    """
    if category in valid_categories:
        return category
    return "Projects"


def _fallback_response(transcript: str) -> dict[str, str]:
    """Generate fallback response when categorization fails."""
    return {
        "category": "Projects",
        "summary": _truncate(transcript),
    }


def _truncate(text: str, max_length: int = 100) -> str:
    """Truncate text to max length."""
    return text[:max_length] if len(text) > max_length else text
