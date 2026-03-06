from unittest.mock import MagicMock, patch

from bot.categorize import categorize_note


class TestCategorizeNote:
    @patch("bot.categorize._get_client")
    def test_categorize_note_success(self, mock_get_client: MagicMock) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"category": "Career", "summary": "Prepare slides for Monday"}'
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = categorize_note("I need to prepare slides for the Monday meeting")

        assert result["category"] == "Career"
        assert result["summary"] == "Prepare slides for Monday"

    @patch("bot.categorize._get_client")
    def test_categorize_note_fitness_category(self, mock_get_client: MagicMock) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"category": "Fitness", "summary": "Go to gym after work"}'
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = categorize_note("Remember to go to the gym after work today")

        assert result["category"] == "Fitness"
        assert result["summary"] == "Go to gym after work"

    @patch("bot.categorize._get_client")
    def test_categorize_note_invalid_category_falls_back(self, mock_get_client: MagicMock) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content='{"category": "InvalidCategory", "summary": "Some task"}')
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = categorize_note("Some random note")

        assert result["category"] == "Projects"
        assert result["summary"] == "Some task"

    @patch("bot.categorize._get_client")
    def test_categorize_note_invalid_json_falls_back(self, mock_get_client: MagicMock) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="This is not valid JSON"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = categorize_note("Call mom tomorrow")

        assert result["category"] == "Projects"
        assert result["summary"] == "Call mom tomorrow"

    @patch("bot.categorize._get_client")
    def test_categorize_note_none_content_falls_back(self, mock_get_client: MagicMock) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content=None))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = categorize_note("Test note")

        assert result["category"] == "Projects"
        assert result["summary"] == "Test note"

    @patch("bot.categorize._get_client")
    def test_categorize_note_long_transcript_truncated(self, mock_get_client: MagicMock) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="invalid json"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        long_transcript = "a" * 150

        result = categorize_note(long_transcript)

        assert result["category"] == "Projects"
        assert len(result["summary"]) == 100

    @patch("bot.categorize._get_client")
    def test_categorize_note_missing_summary_uses_transcript(
        self, mock_get_client: MagicMock
    ) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='{"category": "Health", "summary": ""}'))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = categorize_note("Book dentist appointment")

        assert result["category"] == "Health"
        assert result["summary"] == "Book dentist appointment"
