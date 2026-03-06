# Brain Dump Bot

[![CI](https://github.com/shaibs3/brain-dump-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/shaibs3/brain-dump-bot/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A personal Telegram bot that captures voice notes and text messages throughout the day, transcribes and categorizes them with AI, and sends you a daily summary.

<!-- Add your screenshot here -->
<!-- ![Bot Demo](docs/demo.gif) -->

## Features

- **Voice & Text Notes** - Send voice messages or text, both work seamlessly
- **AI Transcription** - Google Speech-to-Text converts voice to text
- **Smart Categorization** - GPT-4o-mini auto-sorts into life categories
- **Daily Summaries** - Automated summary at your preferred time
- **Todoist Sync** - Optional integration to sync notes as tasks
- **Multi-Language** - Configure any language supported by Google Speech-to-Text
- **Custom Categories** - Define your own categories and emojis
- **Auto Cleanup** - Notes older than 7 days are automatically deleted
- **Single User** - Secured to your Telegram account only

## Default Categories

| Category | Emoji | Examples |
|----------|-------|----------|
| Career | 💼 | Work tasks, meetings, deadlines |
| Health | 🏥 | Doctor appointments, medications |
| Fitness | 💪 | Gym, workouts, exercise |
| Relationships | 👥 | Family, friends, social plans |
| Finance | 💰 | Bills, budgets, purchases |
| Learning | 📚 | Courses, books, skills |
| Projects | 🔧 | Side projects, hobbies |

You can customize these in your `.env` file (see [Configuration](#configuration)).

## Quick Start

### Prerequisites

- Python 3.11+
- Telegram Bot Token ([setup guide](#1-create-telegram-bot))
- Google Cloud Speech-to-Text API ([setup guide](#2-setup-google-cloud-speech-to-text))
- OpenAI API Key ([setup guide](#3-get-openai-api-key))

### Installation

```bash
# Clone the repository
git clone https://github.com/shaibs3/brain-dump-bot.git
cd brain-dump-bot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials (see setup guides below)
```

### Run

```bash
python -m bot.main
```

## Setup Guides

### 1. Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g., "My Brain Dump")
4. Choose a username (must end in `bot`, e.g., `my_brain_dump_bot`)
5. Copy the **API token** → add to `.env` as `TELEGRAM_BOT_TOKEN`

### 2. Setup Google Cloud Speech-to-Text

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select existing)
3. Enable the **Speech-to-Text API**:
   - Go to "APIs & Services" → "Library"
   - Search "Speech-to-Text"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Name it (e.g., "brain-dump-bot")
   - Click "Done"
5. Create key file:
   - Click on your new service account
   - Go to "Keys" tab → "Add Key" → "Create new key"
   - Choose **JSON** → Download
   - Save the file (e.g., `google-credentials.json`)
6. Add path to `.env` as `GOOGLE_APPLICATION_CREDENTIALS`

### 3. Get OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Copy the key → add to `.env` as `OPENAI_API_KEY`

### 4. Get Your Telegram User ID

1. Open Telegram and search for **@userinfobot**
2. Send `/start`
3. Copy your **ID** number → add to `.env` as `ALLOWED_USER_ID`

## Configuration

Edit `.env` with your values:

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-credentials.json
OPENAI_API_KEY=your_openai_key
ALLOWED_USER_ID=123456789

# Optional
SUMMARY_TIME=21:00                    # Daily summary time (24h format)
TIMEZONE=UTC                          # Your timezone (e.g., America/New_York)
LANGUAGE_CODE=en-US                   # Speech recognition language

# Custom categories (format: "Name:emoji,Name:emoji,...")
CATEGORIES=Career:💼,Health:🏥,Fitness:💪,Family:👨‍👩‍👧,Money:💵,Ideas:💡

# Todoist Integration (optional)
TODOIST_API_TOKEN=your_todoist_token
TODOIST_PROJECT_NAME=Brain Dump
```

### Supported Languages

Set `LANGUAGE_CODE` to any [supported language](https://cloud.google.com/speech-to-text/docs/languages):

| Language | Code |
|----------|------|
| English (US) | `en-US` |
| English (UK) | `en-GB` |
| Spanish | `es-ES` |
| French | `fr-FR` |
| German | `de-DE` |
| Hebrew | `he-IL` |
| Chinese | `zh-CN` |
| Japanese | `ja-JP` |

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and usage info |
| `/summary` | Get today's summary |
| `/yesterday` | Get yesterday's summary |
| `/status` | Show today's note count |
| `/settime HH:MM` | Change daily summary time |

## Todoist Integration (Optional)

Sync your notes to Todoist as tasks automatically.

### Setup

1. **Get your API token:**
   - Go to [Todoist Developer Settings](https://todoist.com/app/settings/integrations/developer)
   - Scroll down to "API token"
   - Copy your token

2. **Add to your `.env` file:**
   ```bash
   TODOIST_API_TOKEN=your_api_token_here
   TODOIST_PROJECT_NAME=Brain Dump  # Optional, defaults to "Brain Dump"
   ```

3. **Restart the bot**

### What gets synced

| Event | Todoist Task |
|-------|--------------|
| New voice/text note | Task with category emoji and label (e.g., `💼 Call client about project`) |
| Daily summary | Task titled `📋 Daily Summary - March 6, 2026 (5 notes)` |

## Deployment

### Using systemd (Linux/VPS)

```bash
sudo nano /etc/systemd/system/brain-dump-bot.service
```

```ini
[Unit]
Description=Brain Dump Bot
After=network.target

[Service]
User=your-user
WorkingDirectory=/path/to/brain-dump-bot
Environment="PATH=/path/to/brain-dump-bot/.venv/bin"
ExecStart=/path/to/brain-dump-bot/.venv/bin/python -m bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable brain-dump-bot
sudo systemctl start brain-dump-bot
```

### Auto-Deploy with GitHub Actions (Optional)

To enable automatic deployment on push to main:

1. Add repository variable: `DEPLOY_ENABLED` = `true`
2. Add repository secrets:
   - `VPS_HOST` - Your server IP
   - `VPS_USERNAME` - SSH username
   - `VPS_SSH_KEY` - Private SSH key

## Troubleshooting

### "Unauthorized" error
- Make sure `ALLOWED_USER_ID` matches your Telegram user ID
- Get your ID from @userinfobot

### "Could not transcribe" error
- Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Verify the JSON file exists and is readable
- Ensure Speech-to-Text API is enabled in Google Cloud

### Bot not responding
- Check the bot is running: `sudo systemctl status brain-dump-bot`
- View logs: `journalctl -u brain-dump-bot -f`
- Verify `TELEGRAM_BOT_TOKEN` is correct

### Wrong language transcription
- Set `LANGUAGE_CODE` in `.env` to match your language
- Restart the bot after changing

### Categories not showing correctly
- Check `CATEGORIES` format: `Name:emoji,Name:emoji,...`
- No spaces around colons or commas
- Restart the bot after changing

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest -v

# Linting
ruff check .
ruff format .

# Type checking
mypy .
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest -v`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text)
- [OpenAI](https://openai.com)
