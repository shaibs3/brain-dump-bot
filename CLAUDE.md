# Brain Dump Bot - Claude Code Guidelines

## Before Creating PRs

**Always run all CI checks locally before creating a PR:**

```bash
source .venv/bin/activate

# Lint
ruff check .
ruff format --check .

# Type check
mypy .

# Security scan
bandit -r . -x ./tests,./.venv,./venv,./.git

# Tests
pytest -v
```

All checks must pass before pushing and creating a PR.

## Project Structure

- `bot/` - Telegram bot handlers and logic
- `db/` - Database layer (SQLite)
- `tests/` - Unit tests
- `config.py` - Configuration from environment variables

## Code Style

- Python 3.11+
- Use `X | None` instead of `Optional[X]`
- Use ruff for linting and formatting
- All functions must have type hints
