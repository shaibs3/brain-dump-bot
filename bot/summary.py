from collections import defaultdict
from datetime import date, timedelta

from config import CATEGORIES, CATEGORY_EMOJIS
from db.models import Note


def generate_summary(notes: list[Note], summary_date: date | None = None) -> str:
    """Generate formatted daily summary from notes.

    Args:
        notes: List of notes to summarize
        summary_date: Date for the summary header (defaults to today)

    Returns:
        Formatted summary string
    """
    if summary_date is None:
        summary_date = date.today()

    if not notes:
        return f"📋 Daily Summary - {summary_date:%B %d, %Y}\n\nNo notes recorded today."

    # Group notes by category
    by_category: dict[str, list[str]] = defaultdict(list)
    for note in notes:
        by_category[note.category].append(note.summary)

    # Build message
    lines = [f"📋 Daily Summary - {summary_date:%B %d, %Y}\n"]

    # Maintain consistent category order
    for category in CATEGORIES:
        if category in by_category:
            emoji = CATEGORY_EMOJIS.get(category, "📌")
            lines.append(f"{emoji} {category}")
            for item in by_category[category]:
                lines.append(f"• {item}")
            lines.append("")

    lines.append(f"---\n📊 {len(notes)} notes today")

    return "\n".join(lines)


def generate_yesterday_summary(notes: list[Note]) -> str:
    """Generate summary for yesterday's notes.

    Args:
        notes: List of yesterday's notes

    Returns:
        Formatted summary string for yesterday
    """
    yesterday = date.today() - timedelta(days=1)
    return generate_summary(notes, yesterday)
