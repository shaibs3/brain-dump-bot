from unittest.mock import MagicMock, patch

import pytest

from bot.llm.prompt import (
    build_system_prompt,
    parse_response,
    validate_category,
)


class TestBuildSystemPrompt:
    def test_includes_categories(self) -> None:
        categories = ["Work", "Personal", "Health"]
        prompt = build_system_prompt(categories)

        assert "Work" in prompt
        assert "Personal" in prompt
        assert "Health" in prompt

    def test_includes_json_format(self) -> None:
        prompt = build_system_prompt(["Work"])

        assert '{"category":' in prompt
        assert '"summary":' in prompt


class TestParseResponse:
    def test_valid_json(self) -> None:
        content = '{"category": "Career", "summary": "Do the thing"}'
        result = parse_response(content, "fallback text")

        assert result["category"] == "Career"
        assert result["summary"] == "Do the thing"

    def test_none_content_falls_back(self) -> None:
        result = parse_response(None, "fallback text")

        assert result["category"] == "Projects"
        assert result["summary"] == "fallback text"

    def test_invalid_json_falls_back(self) -> None:
        result = parse_response("not valid json", "fallback text")

        assert result["category"] == "Projects"
        assert result["summary"] == "fallback text"

    def test_missing_category_defaults_to_projects(self) -> None:
        content = '{"summary": "Do the thing"}'
        result = parse_response(content, "fallback")

        assert result["category"] == "Projects"

    def test_missing_summary_uses_transcript(self) -> None:
        content = '{"category": "Health", "summary": ""}'
        result = parse_response(content, "fallback text")

        assert result["summary"] == "fallback text"

    def test_long_transcript_truncated(self) -> None:
        long_text = "a" * 150
        result = parse_response("invalid", long_text)

        assert len(result["summary"]) == 100


class TestValidateCategory:
    def test_valid_category_returned(self) -> None:
        result = validate_category("Health", ["Work", "Health", "Personal"])
        assert result == "Health"

    def test_invalid_category_falls_back_to_projects(self) -> None:
        result = validate_category("InvalidCategory", ["Work", "Health"])
        assert result == "Projects"


class TestOpenAIClient:
    @patch("bot.llm.openai.OpenAI")
    def test_categorize_success(self, mock_openai_class: MagicMock) -> None:
        from bot.llm.openai import OpenAIClient

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(content='{"category": "Career", "summary": "Prepare slides"}')
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        client = OpenAIClient(api_key="test-key")
        result = client.categorize("prepare slides", ["Career", "Health"])

        assert result["category"] == "Career"
        assert result["summary"] == "Prepare slides"

    @patch("bot.llm.openai.OpenAI")
    def test_uses_custom_model(self, mock_openai_class: MagicMock) -> None:
        from bot.llm.openai import OpenAIClient

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content='{"category": "Work", "summary": "x"}'))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        client = OpenAIClient(api_key="test-key", model="gpt-4o")
        client.categorize("test", ["Work"])

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "gpt-4o"


class TestGeminiClient:
    @patch("bot.llm.gemini.genai")
    def test_categorize_success(self, mock_genai: MagicMock) -> None:
        from bot.llm.gemini import GeminiClient

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"category": "Health", "summary": "Book appointment"}'
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        client = GeminiClient(api_key="test-key")
        result = client.categorize("book doctor appointment", ["Career", "Health"])

        assert result["category"] == "Health"
        assert result["summary"] == "Book appointment"

    @patch("bot.llm.gemini.genai")
    def test_uses_custom_model(self, mock_genai: MagicMock) -> None:
        from bot.llm.gemini import GeminiClient

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"category": "Work", "summary": "Test"}'
        mock_client.models.generate_content.return_value = mock_response
        mock_genai.Client.return_value = mock_client

        client = GeminiClient(api_key="test-key", model="gemini-1.5-pro")
        client.categorize("test", ["Work"])

        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-1.5-pro"


class TestGetLLMClient:
    def test_returns_openai_client(self) -> None:
        from bot.llm import get_llm_client, reset_client
        from bot.llm.openai import OpenAIClient

        reset_client()

        with (
            patch("config.OPENAI_API_KEY", "test-key"),
            patch("config.LLM_PROVIDER", "openai"),
            patch("config.LLM_MODEL", None),
            patch("bot.llm.openai.OpenAI"),
        ):
            client = get_llm_client()
            assert isinstance(client, OpenAIClient)

        reset_client()

    def test_returns_gemini_client(self) -> None:
        from bot.llm import get_llm_client, reset_client
        from bot.llm.gemini import GeminiClient

        reset_client()

        with (
            patch("config.GEMINI_API_KEY", "test-key"),
            patch("config.LLM_PROVIDER", "gemini"),
            patch("config.LLM_MODEL", None),
            patch("bot.llm.gemini.genai"),
        ):
            client = get_llm_client()
            assert isinstance(client, GeminiClient)

        reset_client()

    def test_raises_on_unknown_provider(self) -> None:
        from bot.llm import get_llm_client, reset_client

        reset_client()

        with (
            patch("config.LLM_PROVIDER", "unknown"),
            pytest.raises(ValueError, match="Unknown LLM_PROVIDER"),
        ):
            get_llm_client()

        reset_client()
