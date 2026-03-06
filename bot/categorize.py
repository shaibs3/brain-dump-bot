import json

from openai import OpenAI

from config import CATEGORIES, OPENAI_API_KEY

# Lazy-loaded client to avoid errors during test collection
_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Get or create OpenAI client."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


SYSTEM_PROMPT = f"""You are a categorization assistant. Given a transcribed voice note, you must:
1. Categorize it into exactly one of these categories: {", ".join(CATEGORIES)}
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


def categorize_note(transcript: str) -> dict[str, str]:
    """Categorize transcript and generate summary using OpenAI.

    Args:
        transcript: The transcribed voice note text

    Returns:
        Dict with 'category' and 'summary' keys
    """
    client = _get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
        temperature=0.3,
        max_tokens=150,
    )

    content = response.choices[0].message.content
    if content is None:
        return _fallback_response(transcript)

    content = content.strip()

    try:
        result: dict[str, str] = json.loads(content)
        # Validate category
        if result.get("category") not in CATEGORIES:
            result["category"] = "Projects"
        # Ensure summary exists
        if not result.get("summary"):
            result["summary"] = transcript[:100] if len(transcript) > 100 else transcript
        return result
    except json.JSONDecodeError:
        return _fallback_response(transcript)


def _fallback_response(transcript: str) -> dict[str, str]:
    """Generate fallback response when categorization fails."""
    return {
        "category": "Projects",
        "summary": transcript[:100] if len(transcript) > 100 else transcript,
    }
