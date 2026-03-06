from unittest.mock import MagicMock, patch

from bot.transcribe import transcribe_audio


class TestTranscribeAudio:
    @patch("bot.transcribe.speech.SpeechClient")
    def test_transcribe_audio_success(
        self, mock_client_class: MagicMock, tmp_path: MagicMock
    ) -> None:
        # Create a dummy audio file
        audio_file = tmp_path / "test.ogg"
        audio_file.write_bytes(b"fake audio content")

        # Mock the response
        mock_alternative = MagicMock()
        mock_alternative.transcript = "Hello world"

        mock_result = MagicMock()
        mock_result.alternatives = [mock_alternative]

        mock_response = MagicMock()
        mock_response.results = [mock_result]

        mock_client = MagicMock()
        mock_client.recognize.return_value = mock_response
        mock_client_class.return_value = mock_client

        # Call the function
        result = transcribe_audio(str(audio_file))

        # Verify
        assert result == "Hello world"
        mock_client.recognize.assert_called_once()

    @patch("bot.transcribe.speech.SpeechClient")
    def test_transcribe_audio_multiple_results(
        self, mock_client_class: MagicMock, tmp_path: MagicMock
    ) -> None:
        audio_file = tmp_path / "test.ogg"
        audio_file.write_bytes(b"fake audio content")

        # Mock multiple results
        mock_alt1 = MagicMock()
        mock_alt1.transcript = "Hello"

        mock_alt2 = MagicMock()
        mock_alt2.transcript = "world"

        mock_result1 = MagicMock()
        mock_result1.alternatives = [mock_alt1]

        mock_result2 = MagicMock()
        mock_result2.alternatives = [mock_alt2]

        mock_response = MagicMock()
        mock_response.results = [mock_result1, mock_result2]

        mock_client = MagicMock()
        mock_client.recognize.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = transcribe_audio(str(audio_file))

        assert result == "Hello world"

    @patch("bot.transcribe.speech.SpeechClient")
    def test_transcribe_audio_empty_response(
        self, mock_client_class: MagicMock, tmp_path: MagicMock
    ) -> None:
        audio_file = tmp_path / "test.ogg"
        audio_file.write_bytes(b"fake audio content")

        mock_response = MagicMock()
        mock_response.results = []

        mock_client = MagicMock()
        mock_client.recognize.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = transcribe_audio(str(audio_file))

        assert result == ""

    @patch("bot.transcribe.speech.SpeechClient")
    def test_transcribe_audio_no_alternatives(
        self, mock_client_class: MagicMock, tmp_path: MagicMock
    ) -> None:
        audio_file = tmp_path / "test.ogg"
        audio_file.write_bytes(b"fake audio content")

        mock_result = MagicMock()
        mock_result.alternatives = []

        mock_response = MagicMock()
        mock_response.results = [mock_result]

        mock_client = MagicMock()
        mock_client.recognize.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = transcribe_audio(str(audio_file))

        assert result == ""
