from unittest.mock import MagicMock, patch

from bot.todoist import (
    is_todoist_enabled,
    sync_daily_summary_to_todoist,
    sync_note_to_todoist,
)


class TestIsTodoistEnabled:
    @patch("bot.todoist.TODOIST_API_TOKEN", "test_token")
    def test_enabled_when_token_set(self) -> None:
        assert is_todoist_enabled() is True

    @patch("bot.todoist.TODOIST_API_TOKEN", "")
    def test_disabled_when_token_empty(self) -> None:
        assert is_todoist_enabled() is False

    @patch("bot.todoist.TODOIST_API_TOKEN", None)
    def test_disabled_when_token_none(self) -> None:
        assert is_todoist_enabled() is False


class TestSyncNoteToTodoist:
    @patch("bot.todoist.TODOIST_API_TOKEN", "")
    def test_returns_false_when_disabled(self) -> None:
        result = sync_note_to_todoist("Career", "Test summary", "Full transcript")
        assert result is False

    @patch("bot.todoist._project_id", "project123")
    @patch("bot.todoist.TODOIST_API_TOKEN", "test_token")
    @patch("bot.todoist._get_client")
    def test_creates_task_successfully(self, mock_get_client: MagicMock) -> None:
        mock_api = MagicMock()
        mock_get_client.return_value = mock_api

        result = sync_note_to_todoist("Career", "Test summary", "Full transcript")

        assert result is True
        mock_api.add_task.assert_called_once()
        call_kwargs = mock_api.add_task.call_args[1]
        assert "💼 Test summary" in call_kwargs["content"]
        assert call_kwargs["project_id"] == "project123"
        assert "Career" in call_kwargs["labels"]

    @patch("bot.todoist._project_id", "project123")
    @patch("bot.todoist.TODOIST_API_TOKEN", "test_token")
    @patch("bot.todoist._get_client")
    def test_handles_api_error(self, mock_get_client: MagicMock) -> None:
        mock_api = MagicMock()
        mock_api.add_task.side_effect = Exception("API error")
        mock_get_client.return_value = mock_api

        result = sync_note_to_todoist("Career", "Test summary", "Full transcript")

        assert result is False


class TestSyncDailySummaryToTodoist:
    @patch("bot.todoist.TODOIST_API_TOKEN", "")
    def test_returns_false_when_disabled(self) -> None:
        result = sync_daily_summary_to_todoist("Summary text", 5)
        assert result is False

    @patch("bot.todoist._project_id", "project123")
    @patch("bot.todoist.TODOIST_API_TOKEN", "test_token")
    @patch("bot.todoist._get_client")
    def test_creates_summary_task(self, mock_get_client: MagicMock) -> None:
        mock_api = MagicMock()
        mock_get_client.return_value = mock_api

        result = sync_daily_summary_to_todoist("Full summary text", 5)

        assert result is True
        mock_api.add_task.assert_called_once()
        call_kwargs = mock_api.add_task.call_args[1]
        assert "📋 Daily Summary" in call_kwargs["content"]
        assert "5 notes" in call_kwargs["content"]
        assert call_kwargs["description"] == "Full summary text"


class TestGetOrCreateProject:
    @patch("bot.todoist._project_id", None)
    @patch("bot.todoist.TODOIST_API_TOKEN", "test_token")
    @patch("bot.todoist.TODOIST_PROJECT_NAME", "Brain Dump")
    @patch("bot.todoist._get_client")
    def test_finds_existing_project(self, mock_get_client: MagicMock) -> None:
        from bot.todoist import _get_or_create_project

        mock_api = MagicMock()
        mock_project = MagicMock()
        mock_project.name = "Brain Dump"
        mock_project.id = "existing123"
        mock_api.get_projects.return_value = [mock_project]
        mock_get_client.return_value = mock_api

        result = _get_or_create_project(mock_api)

        assert result == "existing123"
        mock_api.add_project.assert_not_called()

    @patch("bot.todoist._project_id", None)
    @patch("bot.todoist.TODOIST_API_TOKEN", "test_token")
    @patch("bot.todoist.TODOIST_PROJECT_NAME", "Brain Dump")
    @patch("bot.todoist._get_client")
    def test_creates_new_project(self, mock_get_client: MagicMock) -> None:
        from bot.todoist import _get_or_create_project

        mock_api = MagicMock()
        mock_api.get_projects.return_value = []  # No existing projects
        mock_new_project = MagicMock()
        mock_new_project.id = "new123"
        mock_api.add_project.return_value = mock_new_project
        mock_get_client.return_value = mock_api

        result = _get_or_create_project(mock_api)

        assert result == "new123"
        mock_api.add_project.assert_called_once_with(name="Brain Dump")
