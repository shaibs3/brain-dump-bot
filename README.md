# Brain Dump Bot

[![CI](https://github.com/shaibs3/brain-dump-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/shaibs3/brain-dump-bot/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A personal Telegram bot that captures voice notes and text messages throughout the day, transcribes and categorizes them with AI, and sends you a daily summary.

## Features

- **Voice & Text Notes** - Send voice messages or text, both work seamlessly
- **AI Transcription** - Google Speech-to-Text converts voice to text
- **Smart Categorization** - GPT-4o-mini auto-sorts into life categories
- **Daily Summaries** - Automated summary at your preferred time
- **Todoist Sync** - Optional integration to sync notes as tasks
- **Auto Cleanup** - Notes older than 7 days are automatically deleted
- **Single User** - Secured to your Telegram account only

## Categories

| Category | Emoji | Examples |
|----------|-------|----------|
| Career | 💼 | Work tasks, meetings, deadlines |
| Health | 🏥 | Doctor appointments, medications |
| Fitness | 💪 | Gym, workouts, exercise |
| Relationships | 👥 | Family, friends, social plans |
| Finance | 💰 | Bills, budgets, purchases |
| Learning | 📚 | Courses, books, skills |
| Projects | 🔧 | Side projects, hobbies |

## Quick Start

### Prerequisites

- Python 3.11+
- [Telegram Bot Token](https://core.telegram.org/bots#creating-a-new-bot) (from @BotFather)
- [Google Cloud Speech-to-Text API](https://cloud.google.com/speech-to-text) credentials
- [OpenAI API Key](https://platform.openai.com/api-keys)
- ffmpeg (`brew install ffmpeg` or `apt install ffmpeg`)

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
# Edit .env with your credentials
```

### Configuration

Edit `.env` with your values:

```bash
# Required
TELEGRAM_BOT_TOKEN=your_bot_token
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-credentials.json
OPENAI_API_KEY=your_openai_key
ALLOWED_USER_ID=your_telegram_user_id  # Get from @userinfobot

# Optional
SUMMARY_TIME=21:00      # Daily summary time (24h format)
TIMEZONE=UTC            # Your timezone

# Optional - Todoist Integration
TODOIST_API_TOKEN=your_todoist_token
TODOIST_PROJECT_NAME=Brain Dump
```

### Run

```bash
python -m bot.main
```

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and usage info |
| `/summary` | Get today's summary |
| `/yesterday` | Get yesterday's summary |
| `/status` | Show today's note count |
| `/settime HH:MM` | Change daily summary time |

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

## Cost Estimates

| Service | Monthly Cost |
|---------|--------------|
| VPS (Oracle Cloud Free) | $0 |
| Google Speech-to-Text | ~$0.50-1 (5-15 notes/day) |
| OpenAI API (gpt-4o-mini) | ~$0.50-1 |
| **Total** | **~$1-2/month** |

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
