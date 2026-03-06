# Brain Dump Bot

A Telegram bot that captures voice notes throughout the day, transcribes them using Google Speech-to-Text, categorizes them with AI, and sends daily summaries.

## Features

- **Voice Note Transcription** - Send voice messages, get instant transcription
- **AI Categorization** - Automatic sorting into Career, Health, Fitness, Relationships, Finance, Learning, Projects
- **Daily Summaries** - Automated summary at configurable time (default 9pm)
- **On-Demand Summary** - Get your summary anytime with `/summary`
- **Single User** - Secured to your Telegram account only

## Prerequisites

- Python 3.11+
- ffmpeg (for audio processing)
- Google Cloud account with Speech-to-Text API enabled
- OpenAI API key
- Telegram bot token (from @BotFather)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shaibs3/brain-dump-bot.git
   cd brain-dump-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your credentials (see Configuration below)

## Configuration

Create a `.env` file with the following variables:

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to Google Cloud service account JSON |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `SUMMARY_TIME` | Daily summary time in HH:MM format (default: 21:00) |
| `TIMEZONE` | Your timezone (default: Asia/Jerusalem) |
| `ALLOWED_USER_ID` | Your Telegram user ID (get from @userinfobot) |

### Getting API Keys

1. **Telegram Bot Token**
   - Message @BotFather on Telegram
   - Send `/newbot` and follow the prompts
   - Copy the token provided

2. **Google Cloud Speech-to-Text**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing
   - Enable the Speech-to-Text API
   - Create a service account with Speech-to-Text permissions
   - Download the JSON key file

3. **OpenAI API Key**
   - Go to [OpenAI Platform](https://platform.openai.com)
   - Create an API key in Settings > API Keys

4. **Your Telegram User ID**
   - Message @userinfobot on Telegram
   - It will reply with your user ID

## Usage

**Run the bot:**
```bash
python -m bot.main
```

**Available commands:**

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and usage info |
| `/summary` | Get today's summary |
| `/yesterday` | Get yesterday's summary |
| `/status` | Show today's note count |
| `/settime HH:MM` | Change daily summary time |

**Voice notes:**
Simply send a voice message to the bot. It will:
1. Transcribe the audio
2. Categorize it automatically
3. Save it for the daily summary
4. Confirm with category and summary

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

## Deployment

### Using systemd (Linux)

1. **Create service file**
   ```bash
   sudo nano /etc/systemd/system/brain-dump-bot.service
   ```

2. **Add configuration**
   ```ini
   [Unit]
   Description=Brain Dump Telegram Bot
   After=network.target

   [Service]
   User=your-user
   WorkingDirectory=/path/to/brain-dump-bot
   Environment="PATH=/path/to/brain-dump-bot/venv/bin"
   ExecStart=/path/to/brain-dump-bot/venv/bin/python -m bot.main
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start**
   ```bash
   sudo systemctl enable brain-dump-bot
   sudo systemctl start brain-dump-bot
   ```

4. **Check status**
   ```bash
   sudo systemctl status brain-dump-bot
   ```

## Development

**Install dev dependencies:**
```bash
pip install -r requirements-dev.txt
```

**Run tests:**
```bash
pytest -v
```

**Run linting:**
```bash
ruff check .
ruff format .
```

**Run type checking:**
```bash
mypy .
```

## Cost Estimates

| Service | Estimated Cost |
|---------|----------------|
| VPS (DigitalOcean/Linode) | ~$5-6/month |
| Google Speech-to-Text | ~$0.50-1/month (5-15 notes/day) |
| OpenAI API (gpt-4o-mini) | ~$0.50-1/month |

## License

MIT
