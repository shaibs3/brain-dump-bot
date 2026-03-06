from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.scheduler import send_daily_summary, setup_scheduler, shutdown_scheduler
from db.models import Note


def _make_note(note_id: int, category: str, summary: str) -> Note:
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


class TestSendDailySummary:
    @pytest.mark.asyncio
    @patch("bot.scheduler.ALLOWED_USER_ID", 12345)
    @patch("bot.scheduler.db")
    async def test_sends_summary_when_notes_exist(self, mock_db: MagicMock) -> None:
        mock_db.get_notes_for_summary.return_value = [
            _make_note(1, "Career", "Test task"),
            _make_note(2, "Health", "Doctor appointment"),
        ]

        mock_app = MagicMock()
        mock_app.bot = AsyncMock()
        mock_app.bot.send_message = AsyncMock()

        await send_daily_summary(mock_app)

        mock_app.bot.send_message.assert_called_once()
        call_kwargs = mock_app.bot.send_message.call_args[1]
        assert call_kwargs["chat_id"] == 12345
        assert "Career" in call_kwargs["text"]
        assert "Health" in call_kwargs["text"]

        mock_db.mark_notes_as_summarized.assert_called_once_with([1, 2])
        mock_db.save_daily_summary.assert_called_once()

    @pytest.mark.asyncio
    @patch("bot.scheduler.ALLOWED_USER_ID", 12345)
    @patch("bot.scheduler.db")
    async def test_skips_when_no_notes(self, mock_db: MagicMock) -> None:
        mock_db.get_notes_for_summary.return_value = []

        mock_app = MagicMock()
        mock_app.bot = AsyncMock()
        mock_app.bot.send_message = AsyncMock()

        await send_daily_summary(mock_app)

        mock_app.bot.send_message.assert_not_called()
        mock_db.mark_notes_as_summarized.assert_not_called()

    @pytest.mark.asyncio
    @patch("bot.scheduler.ALLOWED_USER_ID", 0)
    @patch("bot.scheduler.db")
    async def test_skips_when_no_user_configured(self, mock_db: MagicMock) -> None:
        mock_app = MagicMock()
        mock_app.bot = AsyncMock()

        await send_daily_summary(mock_app)

        mock_db.get_notes_for_summary.assert_not_called()


class TestSetupScheduler:
    @patch("bot.scheduler.AsyncIOScheduler")
    @patch("bot.scheduler.db")
    def test_setup_creates_scheduler(
        self, mock_db: MagicMock, mock_scheduler_class: MagicMock
    ) -> None:
        mock_db.get_setting.return_value = "21:00"
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler

        mock_app = MagicMock()

        setup_scheduler(mock_app)

        mock_scheduler_class.assert_called_once()
        mock_scheduler.add_job.assert_called_once()
        mock_scheduler.start.assert_called_once()

    @patch("bot.scheduler.AsyncIOScheduler")
    @patch("bot.scheduler.db")
    def test_setup_uses_custom_time(
        self, mock_db: MagicMock, mock_scheduler_class: MagicMock
    ) -> None:
        mock_db.get_setting.return_value = "22:30"
        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler

        mock_app = MagicMock()

        setup_scheduler(mock_app)

        # Check that the trigger was created with correct time
        add_job_call = mock_scheduler.add_job.call_args
        trigger = add_job_call[1]["trigger"]
        assert trigger.fields[5].expressions[0].first == 22  # hour
        assert trigger.fields[6].expressions[0].first == 30  # minute


class TestShutdownScheduler:
    @patch("bot.scheduler.scheduler", None)
    def test_shutdown_handles_none(self) -> None:
        # Should not raise
        shutdown_scheduler()

    @patch("bot.scheduler.scheduler")
    def test_shutdown_stops_running_scheduler(self, mock_scheduler: MagicMock) -> None:
        mock_scheduler.running = True

        shutdown_scheduler()

        mock_scheduler.shutdown.assert_called_once()

    @patch("bot.scheduler.scheduler")
    def test_shutdown_skips_if_not_running(self, mock_scheduler: MagicMock) -> None:
        mock_scheduler.running = False

        shutdown_scheduler()

        mock_scheduler.shutdown.assert_not_called()
