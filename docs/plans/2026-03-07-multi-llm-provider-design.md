# Multi-LLM Provider Support Design

**Date:** 2026-03-07
**Status:** Approved

## Overview

Add support for multiple LLM providers (OpenAI and Gemini) with an extensible design for future providers. Users configure their preferred provider via environment variables.

## Configuration

New environment variables:

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `LLM_PROVIDER` | `openai`, `gemini` | `openai` | Which LLM provider to use |
| `LLM_MODEL` | Any valid model name | Provider default | Override default model |
| `GEMINI_API_KEY` | API key string | - | Required if using Gemini |

Default models per provider:
- **OpenAI:** `gpt-4o-mini`
- **Gemini:** `gemini-2.0-flash`

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    config.py                         │
│  LLM_PROVIDER = "openai" | "gemini"                 │
│  LLM_MODEL = optional override                       │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              bot/llm/__init__.py                     │
│  get_llm_client() → LLMClient                       │
│  (factory function based on LLM_PROVIDER)           │
└─────────────────────────────────────────────────────┘
                         │
           ┌─────────────┴─────────────┐
           ▼                           ▼
┌──────────────────────┐    ┌──────────────────────┐
│  bot/llm/openai.py   │    │  bot/llm/gemini.py   │
│  OpenAIClient        │    │  GeminiClient        │
│  implements Protocol │    │  implements Protocol │
└──────────────────────┘    └──────────────────────┘
```

## File Structure

```
bot/
├── llm/
│   ├── __init__.py      # get_llm_client() factory, exports
│   ├── base.py          # LLMClient Protocol definition
│   ├── openai.py        # OpenAIClient implementation
│   ├── gemini.py        # GeminiClient implementation
│   └── prompt.py        # Shared SYSTEM_PROMPT
├── categorize.py        # Simplified, delegates to LLM client
└── ...
```

## Protocol Interface

```python
from typing import Protocol

class LLMClient(Protocol):
    def categorize(self, transcript: str, categories: list[str]) -> dict[str, str]:
        """Categorize transcript and return {"category": str, "summary": str}"""
        ...
```

## Provider Implementations

### OpenAI Client

```python
from openai import OpenAI

class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def categorize(self, transcript: str, categories: list[str]) -> dict[str, str]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": build_system_prompt(categories)},
                {"role": "user", "content": transcript},
            ],
            temperature=0.3,
            max_tokens=150,
        )
        return parse_response(response.choices[0].message.content, transcript)
```

### Gemini Client

```python
import google.generativeai as genai

class GeminiClient:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def categorize(self, transcript: str, categories: list[str]) -> dict[str, str]:
        prompt = build_full_prompt(categories, transcript)
        response = self.model.generate_content(prompt)
        return parse_response(response.text, transcript)
```

## Changes to Existing Files

### config.py

Add:
```python
# LLM Provider configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL")  # None = use provider default
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
```

### bot/categorize.py

Simplify to:
```python
from bot.llm import get_llm_client, LLMClient
from config import CATEGORIES

_client: LLMClient | None = None

def _get_client() -> LLMClient:
    global _client
    if _client is None:
        _client = get_llm_client()
    return _client

def categorize_note(transcript: str) -> dict[str, str]:
    client = _get_client()
    return client.categorize(transcript, CATEGORIES)
```

### requirements.txt

Add:
```
google-generativeai>=0.5.0
```

## Testing Strategy

- Existing tests continue to work (mock at `_get_client` level)
- Add provider-specific unit tests mocking each client's underlying SDK
- Both providers share the same response parsing logic, tested once

## Adding Future Providers

To add a new provider (e.g., Anthropic, Groq):

1. Create `bot/llm/newprovider.py` implementing `LLMClient` protocol
2. Add `NEWPROVIDER_API_KEY` to `config.py`
3. Update factory in `bot/llm/__init__.py` to handle new provider
4. Add tests

## Implementation Order

1. Create `bot/llm/` package with base protocol and prompt
2. Implement OpenAI client (extract from current code)
3. Implement Gemini client
4. Create factory function
5. Update `bot/categorize.py` to use factory
6. Update `config.py` with new env vars
7. Add `google-generativeai` to requirements
8. Update tests
9. Update README with new configuration options
