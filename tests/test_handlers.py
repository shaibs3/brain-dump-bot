from collections.abc import Generator
from datetime import date, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.handlers import (
    handle_text,
    handle_voice,
    settime_command,
    start_command,
    status_command,
    summary_command,
    yesterday_command,
)
from db.models import Note

# Test user ID for authorization
TEST_USER_ID = 12345


@pytest.fixture(autouse=True)
def mock_allowed_user_id() -> Generator[None, Any, None]:
    """Patch ALLOWED_USER_ID for all tests."""
    with patch("bot.handlers.ALLOWED_USER_ID", TEST_USER_ID):
        yield


@pytest.fixture
def mock_update() -> MagicMock:
    """Create a mock Update object."""
    update = MagicMock()
    update.effective_user = MagicMock()
    update.effective_user.id = TEST_USER_ID  # Matches patched ALLOWED_USER_ID
    update.message = MagicMock()
    update.message.reply_text = AsyncMock()
    update.message.message_id = 123
    return update


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock Context object."""
    context = MagicMock()
    context.args = []
    context.bot = AsyncMock()
    return context


class TestStartCommand:
    @pytest.mark.asyncio
    async def test_start_sends_welcome(
        self, mock_update: MagicMock, mock_context: MagicMock
    ) -> None:
        await start_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Brain Dump Bot" in call_args
        assert "/summary" in call_args


class TestSummaryCommand:
    @pytest.mark.asyncio
    @patch("bot.handlers.db")
    async def test_summary_with_no_notes(
        self, mock_db: MagicMock, mock_update: MagicMock, mock_context: MagicMock
    ) -> None:
        mock_db.get_all_notes_for_date.return_value = []

        await summary_command(mock_update, mock_context)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "No notes recorded today" in call_args

    @pytest.mark.asyncio
    @patch("bot.handlers.db")
    async def test_summary_with_notes(
        self, mock_db: MagicMock, mock_update: MagicMock, mock_context: MagicMock
    ) -> None:
        mock_db.get_all_notes_for_date.return_value = [
            Note(
                id=1,
                telegram_message_id=1,
                audio_file_id="file_1",
                transcript="Test",
                category="Career",
                summary="Test task",
                created_at=datetime.now(),
                included_in_summary_at=None,
            )
        ]

        await summary_command(mock_update, mock_context)

        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Career" in call_args
        assert "Test task" in call_args


class TestYesterdayCommand:
    @pytest.mark.asyncio
    @patch("bot.handlers.db")
    async def test_yesterday_command(
        self, mock_db: MagicMock, mock_update: MagicMock, mock_context: MagicMock
    ) -> None:
        mock_db.get_all_notes_for_date.return_value = []

        await yesterday_command(mock_update, mock_context)

        mock_db.get_all_notes_for_date.assert_called_once()
        # Verify it was called with yesterday's date
        call_date = mock_db.get_all_notes_for_date.call_args[0][0]
        assert call_date == date.today() - __import__("datetime").timedelta(days=1)


class TestStatusCommand:
    @pytest.mark.asyncio
    @patch("bot.handlers.db")
    async def test_status_no_notes(
        self, mock_db: MagicMock, mock_update: MagicMock, mock_context: MagicMock
    ) -> None:
        mock_db.get_today_notes_count.return_value = 0

        await status_command(mock_update, mock_context)

        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "No notes recorded today" in call_args

    @pytest.mark.asyncio
    @patch("bot.handlers.db")
    async def test_status_with_notes(
        self, mock_db: MagicMock, mock_update: MagicMock, mock_context: MagicMock
    ) -> None:
        mock_db.get_today_notes_count.return_value = 5
        mock_db.get_last_note_time.return_value = datetime(2026, 3, 6, 14, 30)

        await status_command(mock_update, mock_context)

        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Notes: 5" in call_args
        assert "14:30" in call_args


class TestSettimeCommand:
    @pytest.mark.asyncio
    @patch("bot.handlers.db")
    async def test_settime_no_args_shows_current(
        self, mock_db: MagicMock, mock_update: MagicMock, mock_context: MagicMock
    ) -> None:
        mock_db.get_setting.return_value = "21:00"
        mock_context.args = []

        await settime_command(mock_update, mock_context)

        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "21:00" in call_args
        assert "Usage:" in call_args

    @pytest.mark.asyncio
    @patch("bot.handlers.db")
    async def test_settime_valid_time(
        self, mock_db: MagicMock, mock_update: MagicMock, mock_context: MagicMock
    ) -> None:
        mock_context.args = ["22:30"]

        await settime_command(mock_update, mock_context)

        mock_db.set_setting.assert_called_once_with("summary_time", "22:30")
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "✅" in call_args
        assert "22:30" in call_args

    @pytest.mark.asyncio
    @patch("bot.handlers.db")
    async def test_settime_invalid_format(
        self, mock_db: MagicMock, mock_update: MagicMock, mock_context: MagicMock
    ) -> None:
        mock_context.args = ["invalid"]

        await settime_command(mock_update, mock_context)

        mock_db.set_setting.assert_not_called()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "❌" in call_args

    @pytest.mark.asyncio
    @patch("bot.handlers.db")
    async def test_settime_invalid_range(
        self, mock_db: MagicMock, mock_update: MagicMock, mock_context: MagicMock
    ) -> None:
        mock_context.args = ["25:00"]

        await settime_command(mock_update, mock_context)

        mock_db.set_setting.assert_not_called()


class TestHandleVoice:
    @pytest.mark.asyncio
    @patch("bot.handlers.os.unlink")
    @patch("bot.handlers.transcribe_audio")
    @patch("bot.handlers.categorize_note")
    @patch("bot.handlers.db")
    async def test_handle_voice_success(
        self,
        mock_db: MagicMock,
        mock_categorize: MagicMock,
        mock_transcribe: MagicMock,
        mock_unlink: MagicMock,
        mock_update: MagicMock,
        mock_context: MagicMock,
    ) -> None:
        # Setup mocks
        mock_update.message.voice = MagicMock()
        mock_update.message.voice.file_id = "test_file_id"

        mock_file = AsyncMock()
        mock_context.bot.get_file.return_value = mock_file

        processing_msg = AsyncMock()
        mock_update.message.reply_text.return_value = processing_msg

        mock_transcribe.return_value = "Test transcript"
        mock_categorize.return_value = {"category": "Career", "summary": "Test task"}

        await handle_voice(mock_update, mock_context)

        # Verify flow
        mock_transcribe.assert_called_once()
        mock_categorize.assert_called_once_with("Test transcript")
        mock_db.save_note.assert_called_once()
        processing_msg.edit_text.assert_called()
        final_message = processing_msg.edit_text.call_args[0][0]
        assert "✅" in final_message
        assert "Career" in final_message

    @pytest.mark.asyncio
    @patch("bot.handlers.os.unlink")
    @patch("bot.handlers.transcribe_audio")
    @patch("bot.handlers.db")
    async def test_handle_voice_empty_transcript(
        self,
        mock_db: MagicMock,
        mock_transcribe: MagicMock,
        mock_unlink: MagicMock,
        mock_update: MagicMock,
        mock_context: MagicMock,
    ) -> None:
        mock_update.message.voice = MagicMock()
        mock_update.message.voice.file_id = "test_file_id"

        mock_file = AsyncMock()
        mock_context.bot.get_file.return_value = mock_file

        processing_msg = AsyncMock()
        mock_update.message.reply_text.return_value = processing_msg

        mock_transcribe.return_value = ""

        await handle_voice(mock_update, mock_context)

        mock_db.save_note.assert_not_called()
        final_message = processing_msg.edit_text.call_args[0][0]
        assert "❌" in final_message
        assert "transcribe" in final_message.lower()


class TestHandleText:
    @pytest.mark.asyncio
    @patch("bot.handlers.categorize_note")
    @patch("bot.handlers.db")
    async def test_handle_text_success(
        self,
        mock_db: MagicMock,
        mock_categorize: MagicMock,
        mock_update: MagicMock,
        mock_context: MagicMock,
    ) -> None:
        mock_update.message.text = "Remember to call mom tomorrow"
        mock_categorize.return_value = {"category": "Relationships", "summary": "Call mom tomorrow"}

        await handle_text(mock_update, mock_context)

        mock_categorize.assert_called_once_with("Remember to call mom tomorrow")
        mock_db.save_note.assert_called_once()
        mock_update.message.reply_text.assert_called()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "✅" in call_args
        assert "Relationships" in call_args

    @pytest.mark.asyncio
    @patch("bot.handlers.categorize_note")
    @patch("bot.handlers.db")
    async def test_handle_text_skips_commands(
        self,
        mock_db: MagicMock,
        mock_categorize: MagicMock,
        mock_update: MagicMock,
        mock_context: MagicMock,
    ) -> None:
        mock_update.message.text = "/summary"

        await handle_text(mock_update, mock_context)

        mock_categorize.assert_not_called()
        mock_db.save_note.assert_not_called()
