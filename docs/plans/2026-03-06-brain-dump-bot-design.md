# Brain Dump Bot Design

A Telegram bot that receives voice notes throughout the day, transcribes them using Google Speech-to-Text, auto-categorizes them using an LLM, and sends a daily summary.

## Architecture

```
┌─────────────────┐     ┌─────────────────────────────────────┐
│   You on        │     │            VPS Server               │
│   Telegram      │     │  ┌─────────────────────────────┐   │
│                 │────▶│  │    Telegram Bot (Python)    │   │
│  Voice note     │     │  │    - python-telegram-bot    │   │
│  /summary       │     │  └──────────┬──────────────────┘   │
└─────────────────┘     │             │                       │
                        │             ▼                       │
                        │  ┌──────────────────────────────┐  │
                        │  │   Google Speech-to-Text API  │  │
                        │  └──────────┬───────────────────┘  │
                        │             │                       │
                        │             ▼                       │
                        │  ┌──────────────────────────────┐  │
                        │  │   OpenAI/Claude API          │  │
                        │  │   (categorization)           │  │
                        │  └──────────┬───────────────────┘  │
                        │             │                       │
                        │             ▼                       │
                        │  ┌──────────────────────────────┐  │
                        │  │   SQLite Database            │  │
                        │  │   (notes + transcripts)      │  │
                        │  └──────────────────────────────┘  │
                        │                                     │
                        │  ┌──────────────────────────────┐  │
                        │  │   Scheduler (APScheduler)    │  │
                        │  │   - Daily summary at 9pm     │  │
                        │  └──────────────────────────────┘  │
                        └─────────────────────────────────────┘
```

## Flow

1. User sends a voice note to the bot
2. Bot downloads the audio, sends to Google Speech-to-Text
3. Transcription goes to an LLM for categorization
4. Stored in SQLite with category and timestamp
5. Scheduler triggers daily summary; `/summary` available anytime

## Database Schema

```sql
-- Voice notes table
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_message_id INTEGER,
    audio_file_id TEXT,
    transcript TEXT,
    category TEXT,
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    included_in_summary_at TIMESTAMP
);

-- Daily summaries table
CREATE TABLE daily_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summary_text TEXT,
    notes_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Settings table
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

## Categories

- Career
- Health
- Relationships
- Finance
- Learning
- Projects

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message, brief usage instructions |
| `/summary` | Get summary of today's notes so far |
| `/yesterday` | Get yesterday's summary |
| `/status` | Show count of notes today, last note time |
| `/settime HH:MM` | Change daily summary time (default: 21:00) |

## Voice Note Handling

1. Reply with "Processing..." (immediate feedback)
2. Download audio from Telegram
3. Convert to format Google accepts (if needed)
4. Send to Speech-to-Text API
5. Send transcript to LLM for categorization
6. Save to database
7. Update message: "Saved to **Category**: *summary*"

## Daily Summary Format

```
Daily Summary - March 6, 2026

Career
• Follow up with client about proposal
• Prepare slides for Monday meeting

Health
• Book dentist appointment
• Try that new gym class

Relationships
• Call mom this weekend

---
6 notes today
```

## Project Structure

```
brain-dump-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py
│   ├── handlers.py
│   ├── transcribe.py
│   ├── categorize.py
│   └── scheduler.py
├── db/
│   ├── __init__.py
│   ├── models.py
│   └── brain_dump.db
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Dependencies

```
python-telegram-bot>=20.0
google-cloud-speech>=2.0
openai>=1.0
apscheduler>=3.10
python-dotenv>=1.0
pydub>=0.25
```

## Environment Variables

```
TELEGRAM_BOT_TOKEN=
GOOGLE_APPLICATION_CREDENTIALS=
OPENAI_API_KEY=
SUMMARY_TIME=21:00
TIMEZONE=Asia/Jerusalem
```

## Deployment

- Platform: Small VPS (DigitalOcean/Linode/Hetzner ~$5-6/month)
- Process manager: systemd
- Dependencies: Python 3.11+, ffmpeg

## Estimated Costs

- VPS: ~$5-6/month
- Google Speech-to-Text: ~$0.50-1/month
- LLM API: ~$0.50-1/month
