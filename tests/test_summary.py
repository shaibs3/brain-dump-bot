from datetime import date, datetime

from bot.summary import generate_summary, generate_yesterday_summary
from db.models import Note


def _make_note(
    category: str,
    summary: str,
    note_id: int = 1,
) -> Note:
    """Helper to create a Note for testing."""
    return Note(
        id=note_id,
        telegram_message_id=note_id,
        audio_file_id=f"file_{note_id}",
        transcript=summary,
        category=category,
        summary=summary,
        created_at=datetime.now(),
        included_in_summary_at=None,
    )


class TestGenerateSummary:
    def test_empty_notes(self) -> None:
        result = generate_summary([], date(2026, 3, 6))

        assert "Daily Summary - March 06, 2026" in result
        assert "No notes recorded today" in result

    def test_single_note(self) -> None:
        notes = [_make_note("Career", "Prepare slides for Monday")]

        result = generate_summary(notes, date(2026, 3, 6))

        assert "Daily Summary - March 06, 2026" in result
        assert "💼 Career" in result
        assert "• Prepare slides for Monday" in result
        assert "1 notes today" in result

    def test_multiple_notes_same_category(self) -> None:
        notes = [
            _make_note("Career", "Prepare slides", note_id=1),
            _make_note("Career", "Send email to client", note_id=2),
        ]

        result = generate_summary(notes, date(2026, 3, 6))

        assert "💼 Career" in result
        assert "• Prepare slides" in result
        assert "• Send email to client" in result
        assert "2 notes today" in result

    def test_multiple_categories(self) -> None:
        notes = [
            _make_note("Career", "Prepare slides", note_id=1),
            _make_note("Health", "Book dentist", note_id=2),
            _make_note("Fitness", "Go to gym", note_id=3),
        ]

        result = generate_summary(notes, date(2026, 3, 6))

        assert "💼 Career" in result
        assert "🏥 Health" in result
        assert "💪 Fitness" in result
        assert "3 notes today" in result

    def test_categories_in_correct_order(self) -> None:
        # Add notes in reverse order
        notes = [
            _make_note("Projects", "Side project", note_id=1),
            _make_note("Career", "Work task", note_id=2),
        ]

        result = generate_summary(notes, date(2026, 3, 6))

        # Career should appear before Projects in the output
        career_pos = result.find("Career")
        projects_pos = result.find("Projects")
        assert career_pos < projects_pos

    def test_default_date_is_today(self) -> None:
        notes = [_make_note("Career", "Task")]

        result = generate_summary(notes)

        today = date.today()
        assert f"{today:%B}" in result  # Month name should be present


class TestGenerateYesterdaySummary:
    def test_yesterday_date(self) -> None:
        notes = [_make_note("Career", "Yesterday task")]

        result = generate_yesterday_summary(notes)

        from datetime import timedelta

        yesterday = date.today() - timedelta(days=1)
        assert f"{yesterday:%B}" in result
        assert f"{yesterday:%d}" in result
