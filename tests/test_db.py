import tempfile
from collections.abc import Generator
from datetime import date, datetime
from pathlib import Path

import pytest

from db import Database


@pytest.fixture
def db() -> Generator[Database, None, None]:
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        yield Database(str(db_path))


class TestDatabase:
    def test_save_and_retrieve_note(self, db: Database) -> None:
        note_id = db.save_note(
            telegram_message_id=123,
            audio_file_id="file_abc",
            transcript="Call mom tomorrow",
            category="Relationships",
            summary="Call mom tomorrow",
        )

        assert note_id > 0

        notes = db.get_all_notes_for_date(date.today())
        assert len(notes) == 1
        assert notes[0].transcript == "Call mom tomorrow"
        assert notes[0].category == "Relationships"

    def test_get_notes_for_summary_excludes_summarized(self, db: Database) -> None:
        # Save two notes
        id1 = db.save_note(
            telegram_message_id=1,
            audio_file_id="file_1",
            transcript="Note 1",
            category="Career",
            summary="Note 1",
        )
        db.save_note(
            telegram_message_id=2,
            audio_file_id="file_2",
            transcript="Note 2",
            category="Health",
            summary="Note 2",
        )

        # Mark first as summarized
        db.mark_notes_as_summarized([id1])

        # Only second should appear
        notes = db.get_notes_for_summary(date.today())
        assert len(notes) == 1
        assert notes[0].summary == "Note 2"

    def test_get_all_notes_includes_summarized(self, db: Database) -> None:
        id1 = db.save_note(
            telegram_message_id=1,
            audio_file_id="file_1",
            transcript="Note 1",
            category="Career",
            summary="Note 1",
        )
        db.save_note(
            telegram_message_id=2,
            audio_file_id="file_2",
            transcript="Note 2",
            category="Health",
            summary="Note 2",
        )

        db.mark_notes_as_summarized([id1])

        # Both should appear
        notes = db.get_all_notes_for_date(date.today())
        assert len(notes) == 2

    def test_save_daily_summary(self, db: Database) -> None:
        summary_id = db.save_daily_summary("Test summary", 5)
        assert summary_id > 0

    def test_get_today_notes_count(self, db: Database) -> None:
        assert db.get_today_notes_count() == 0

        db.save_note(
            telegram_message_id=1,
            audio_file_id="file_1",
            transcript="Note 1",
            category="Career",
            summary="Note 1",
        )

        assert db.get_today_notes_count() == 1

    def test_get_last_note_time(self, db: Database) -> None:
        assert db.get_last_note_time() is None

        db.save_note(
            telegram_message_id=1,
            audio_file_id="file_1",
            transcript="Note 1",
            category="Career",
            summary="Note 1",
        )

        last_time = db.get_last_note_time()
        assert last_time is not None
        assert isinstance(last_time, datetime)

    def test_settings(self, db: Database) -> None:
        # Default value
        assert db.get_setting("nonexistent", "default") == "default"
        assert db.get_setting("nonexistent") is None

        # Set and get
        db.set_setting("summary_time", "21:00")
        assert db.get_setting("summary_time") == "21:00"

        # Update
        db.set_setting("summary_time", "22:00")
        assert db.get_setting("summary_time") == "22:00"

    def test_mark_empty_list_does_nothing(self, db: Database) -> None:
        # Should not raise
        db.mark_notes_as_summarized([])
