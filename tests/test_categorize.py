from unittest.mock import MagicMock, patch

from bot.categorize import categorize_note


class TestCategorizeNote:
    @patch("bot.categorize._get_client")
    def test_categorize_note_success(self, mock_get_client: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.categorize.return_value = {
            "category": "Career",
            "summary": "Prepare slides for Monday",
        }
        mock_get_client.return_value = mock_client

        result = categorize_note("I need to prepare slides for the Monday meeting")

        assert result["category"] == "Career"
        assert result["summary"] == "Prepare slides for Monday"

    @patch("bot.categorize._get_client")
    def test_categorize_note_fitness_category(self, mock_get_client: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.categorize.return_value = {
            "category": "Fitness",
            "summary": "Go to gym after work",
        }
        mock_get_client.return_value = mock_client

        result = categorize_note("Remember to go to the gym after work today")

        assert result["category"] == "Fitness"
        assert result["summary"] == "Go to gym after work"

    @patch("bot.categorize._get_client")
    def test_categorize_note_calls_client_with_categories(self, mock_get_client: MagicMock) -> None:
        mock_client = MagicMock()
        mock_client.categorize.return_value = {
            "category": "Projects",
            "summary": "Test",
        }
        mock_get_client.return_value = mock_client

        categorize_note("Test note")

        mock_client.categorize.assert_called_once()
        call_args = mock_client.categorize.call_args
        assert call_args[0][0] == "Test note"
        assert isinstance(call_args[0][1], list)
