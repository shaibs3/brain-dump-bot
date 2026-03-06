# Brain Dump Bot Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Telegram bot that transcribes voice notes, categorizes them with AI, and sends daily summaries.

**Architecture:** Python bot using python-telegram-bot for Telegram integration, Google Speech-to-Text for transcription, OpenAI for categorization, SQLite for storage, and APScheduler for daily summaries.

**Tech Stack:** Python 3.11+, python-telegram-bot, google-cloud-speech, openai, apscheduler, pydub, SQLite

---

### Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `config.py`

**Step 1: Create requirements.txt**

```
python-telegram-bot>=20.0
google-cloud-speech>=2.0
openai>=1.0
apscheduler>=3.10
python-dotenv>=1.0
pydub>=0.25
```

**Step 2: Create .env.example**

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
OPENAI_API_KEY=your_openai_api_key
SUMMARY_TIME=21:00
TIMEZONE=Asia/Jerusalem
ALLOWED_USER_ID=your_telegram_user_id
```

**Step 3: Create .gitignore**

```
.env
*.pyc
__pycache__/
db/*.db
*.log
.venv/
venv/
```

**Step 4: Create config.py**

```python
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUMMARY_TIME = os.getenv("SUMMARY_TIME", "21:00")
TIMEZONE = os.getenv("TIMEZONE", "Asia/Jerusalem")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))

CATEGORIES = ["Career", "Health", "Relationships", "Finance", "Learning", "Projects"]
CATEGORY_EMOJIS = {
    "Career": "💼",
    "Health": "💪",
    "Relationships": "👥",
    "Finance": "💰",
    "Learning": "📚",
    "Projects": "🔧",
}
```

**Step 5: Commit**

```bash
git add requirements.txt .env.example .gitignore config.py
git commit -m "feat: add project configuration files"
```

---

### Task 2: Database Layer

**Files:**
- Create: `db/__init__.py`
- Create: `db/models.py`

**Step 1: Create db/__init__.py**

```python
from .models import Database

__all__ = ["Database"]
```

**Step 2: Create db/models.py**

```python
import sqlite3
from datetime import datetime, date
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class Note:
    id: int
    telegram_message_id: int
    audio_file_id: str
    transcript: str
    category: str
    summary: str
    created_at: datetime
    included_in_summary_at: Optional[datetime]


class Database:
    def __init__(self, db_path: str = "db/brain_dump.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_message_id INTEGER,
                    audio_file_id TEXT,
                    transcript TEXT,
                    category TEXT,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    included_in_summary_at TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS daily_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary_text TEXT,
                    notes_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
            """)

    def save_note(
        self,
        telegram_message_id: int,
        audio_file_id: str,
        transcript: str,
        category: str,
        summary: str,
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO notes (telegram_message_id, audio_file_id, transcript, category, summary)
                VALUES (?, ?, ?, ?, ?)
                """,
                (telegram_message_id, audio_file_id, transcript, category, summary),
            )
            return cursor.lastrowid

    def get_notes_for_summary(self, for_date: Optional[date] = None) -> list[Note]:
        if for_date is None:
            for_date = date.today()

        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM notes
                WHERE date(created_at) = ?
                AND included_in_summary_at IS NULL
                ORDER BY created_at
                """,
                (for_date.isoformat(),),
            ).fetchall()

            return [
                Note(
                    id=row["id"],
                    telegram_message_id=row["telegram_message_id"],
                    audio_file_id=row["audio_file_id"],
                    transcript=row["transcript"],
                    category=row["category"],
                    summary=row["summary"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    included_in_summary_at=None,
                )
                for row in rows
            ]

    def get_all_notes_for_date(self, for_date: Optional[date] = None) -> list[Note]:
        if for_date is None:
            for_date = date.today()

        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM notes
                WHERE date(created_at) = ?
                ORDER BY created_at
                """,
                (for_date.isoformat(),),
            ).fetchall()

            return [
                Note(
                    id=row["id"],
                    telegram_message_id=row["telegram_message_id"],
                    audio_file_id=row["audio_file_id"],
                    transcript=row["transcript"],
                    category=row["category"],
                    summary=row["summary"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    included_in_summary_at=datetime.fromisoformat(row["included_in_summary_at"])
                    if row["included_in_summary_at"]
                    else None,
                )
                for row in rows
            ]

    def mark_notes_as_summarized(self, note_ids: list[int]):
        if not note_ids:
            return
        with self._get_connection() as conn:
            placeholders = ",".join("?" * len(note_ids))
            conn.execute(
                f"""
                UPDATE notes
                SET included_in_summary_at = CURRENT_TIMESTAMP
                WHERE id IN ({placeholders})
                """,
                note_ids,
            )

    def save_daily_summary(self, summary_text: str, notes_count: int) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO daily_summaries (summary_text, notes_count)
                VALUES (?, ?)
                """,
                (summary_text, notes_count),
            )
            return cursor.lastrowid

    def get_today_notes_count(self) -> int:
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*) as count FROM notes
                WHERE date(created_at) = date('now')
                """
            ).fetchone()
            return row["count"]

    def get_last_note_time(self) -> Optional[datetime]:
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT created_at FROM notes
                WHERE date(created_at) = date('now')
                ORDER BY created_at DESC
                LIMIT 1
                """
            ).fetchone()
            return datetime.fromisoformat(row["created_at"]) if row else None

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
                """,
                (key, value),
            )
```

**Step 3: Commit**

```bash
git add db/
git commit -m "feat: add database layer with SQLite"
```

---

### Task 3: Google Speech-to-Text Integration

**Files:**
- Create: `bot/__init__.py`
- Create: `bot/transcribe.py`

**Step 1: Create bot/__init__.py**

```python
```

**Step 2: Create bot/transcribe.py**

```python
from google.cloud import speech
from pathlib import Path
import io


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file using Google Speech-to-Text."""
    client = speech.SpeechClient()

    audio_file = Path(audio_path)
    with io.open(audio_file, "rb") as f:
        content = f.read()

    audio = speech.RecognitionAudio(content=content)

    # Telegram voice notes are OGG with OPUS codec
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
        sample_rate_hertz=48000,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )

    response = client.recognize(config=config, audio=audio)

    transcript_parts = []
    for result in response.results:
        transcript_parts.append(result.alternatives[0].transcript)

    return " ".join(transcript_parts)
```

**Step 3: Commit**

```bash
git add bot/
git commit -m "feat: add Google Speech-to-Text transcription"
```

---

### Task 4: LLM Categorization

**Files:**
- Create: `bot/categorize.py`

**Step 1: Create bot/categorize.py**

```python
import json
from openai import OpenAI
from config import OPENAI_API_KEY, CATEGORIES

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = f"""You are a categorization assistant. Given a transcribed voice note, you must:
1. Categorize it into exactly one of these categories: {', '.join(CATEGORIES)}
2. Write a concise one-line summary (max 100 characters)

Respond ONLY with valid JSON in this format:
{{"category": "CategoryName", "summary": "One line summary"}}

Rules:
- If the note doesn't clearly fit a category, use "Projects" as default
- The summary should be actionable when possible (start with verb)
- Keep the summary brief and clear
"""


def categorize_note(transcript: str) -> dict:
    """Categorize transcript and generate summary using OpenAI."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
        temperature=0.3,
        max_tokens=150,
    )

    content = response.choices[0].message.content.strip()

    try:
        result = json.loads(content)
        # Validate category
        if result.get("category") not in CATEGORIES:
            result["category"] = "Projects"
        return result
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {
            "category": "Projects",
            "summary": transcript[:100] if len(transcript) > 100 else transcript,
        }
```

**Step 2: Commit**

```bash
git add bot/categorize.py
git commit -m "feat: add LLM categorization with OpenAI"
```

---

### Task 5: Summary Generator

**Files:**
- Create: `bot/summary.py`

**Step 1: Create bot/summary.py**

```python
from datetime import date, timedelta
from collections import defaultdict
from db.models import Note
from config import CATEGORY_EMOJIS, CATEGORIES


def generate_summary(notes: list[Note], summary_date: date = None) -> str:
    """Generate formatted daily summary from notes."""
    if summary_date is None:
        summary_date = date.today()

    if not notes:
        return f"📋 Daily Summary - {summary_date:%B %d, %Y}\n\nNo notes recorded today."

    # Group notes by category
    by_category = defaultdict(list)
    for note in notes:
        by_category[note.category].append(note.summary)

    # Build message
    lines = [f"📋 Daily Summary - {summary_date:%B %d, %Y}\n"]

    # Maintain consistent category order
    for category in CATEGORIES:
        if category in by_category:
            emoji = CATEGORY_EMOJIS.get(category, "📌")
            lines.append(f"{emoji} {category}")
            for item in by_category[category]:
                lines.append(f"• {item}")
            lines.append("")

    lines.append(f"---\n📊 {len(notes)} notes today")

    return "\n".join(lines)


def generate_summary_for_yesterday(notes: list[Note]) -> str:
    """Generate summary for yesterday's notes."""
    yesterday = date.today() - timedelta(days=1)
    return generate_summary(notes, yesterday)
```

**Step 2: Commit**

```bash
git add bot/summary.py
git commit -m "feat: add summary generator"
```

---

### Task 6: Telegram Handlers

**Files:**
- Create: `bot/handlers.py`

**Step 1: Create bot/handlers.py**

```python
import os
import tempfile
from datetime import date, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from config import ALLOWED_USER_ID, CATEGORY_EMOJIS
from db.models import Database
from bot.transcribe import transcribe_audio
from bot.categorize import categorize_note
from bot.summary import generate_summary


db = Database()


def authorized_only(func):
    """Decorator to restrict bot to authorized user only."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if ALLOWED_USER_ID and update.effective_user.id != ALLOWED_USER_ID:
            await update.message.reply_text("⛔ Unauthorized")
            return
        return await func(update, context)
    return wrapper


@authorized_only
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "🧠 Brain Dump Bot\n\n"
        "Send me voice notes throughout the day. I'll transcribe, categorize, "
        "and send you a daily summary at 9pm.\n\n"
        "Commands:\n"
        "/summary - Get today's summary\n"
        "/yesterday - Get yesterday's summary\n"
        "/status - See today's stats\n"
        "/settime HH:MM - Change summary time"
    )


@authorized_only
async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /summary command - show today's notes."""
    notes = db.get_all_notes_for_date(date.today())
    summary_text = generate_summary(notes)
    await update.message.reply_text(summary_text)


@authorized_only
async def yesterday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /yesterday command."""
    yesterday = date.today() - timedelta(days=1)
    notes = db.get_all_notes_for_date(yesterday)
    summary_text = generate_summary(notes, yesterday)
    await update.message.reply_text(summary_text)


@authorized_only
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command."""
    count = db.get_today_notes_count()
    last_time = db.get_last_note_time()

    if count == 0:
        await update.message.reply_text("📊 No notes recorded today yet.")
    else:
        last_str = last_time.strftime("%H:%M") if last_time else "unknown"
        await update.message.reply_text(
            f"📊 Today's Stats\n\n"
            f"Notes: {count}\n"
            f"Last note: {last_str}"
        )


@authorized_only
async def settime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settime command."""
    if not context.args:
        current = db.get_setting("summary_time", "21:00")
        await update.message.reply_text(
            f"Current summary time: {current}\n"
            f"Usage: /settime HH:MM (e.g., /settime 21:00)"
        )
        return

    time_str = context.args[0]
    try:
        # Validate format
        hours, minutes = time_str.split(":")
        if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
            raise ValueError()

        db.set_setting("summary_time", time_str)
        await update.message.reply_text(f"✅ Summary time set to {time_str}")
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Invalid format. Use HH:MM (e.g., 21:00)")


@authorized_only
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming voice notes."""
    processing_msg = await update.message.reply_text("🎤 Processing...")

    try:
        # Download voice note
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            await file.download_to_drive(tmp.name)
            tmp_path = tmp.name

        try:
            # Transcribe
            transcript = transcribe_audio(tmp_path)

            if not transcript:
                await processing_msg.edit_text("❌ Couldn't transcribe. Try speaking more clearly.")
                return

            # Categorize
            result = categorize_note(transcript)
            category = result["category"]
            summary = result["summary"]

            # Save to database
            db.save_note(
                telegram_message_id=update.message.message_id,
                audio_file_id=voice.file_id,
                transcript=transcript,
                category=category,
                summary=summary,
            )

            # Confirm
            emoji = CATEGORY_EMOJIS.get(category, "📌")
            await processing_msg.edit_text(f"✅ Saved to {emoji} {category}:\n{summary}")

        finally:
            os.unlink(tmp_path)

    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {str(e)}")
```

**Step 2: Commit**

```bash
git add bot/handlers.py
git commit -m "feat: add Telegram command and voice handlers"
```

---

### Task 7: Scheduler

**Files:**
- Create: `bot/scheduler.py`

**Step 1: Create bot/scheduler.py**

```python
from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application
from config import SUMMARY_TIME, TIMEZONE, ALLOWED_USER_ID
from db.models import Database
from bot.summary import generate_summary

db = Database()
scheduler = AsyncIOScheduler(timezone=TIMEZONE)


async def send_daily_summary(app: Application):
    """Send daily summary to user."""
    if not ALLOWED_USER_ID:
        return

    notes = db.get_notes_for_summary(date.today())

    if not notes:
        return  # No notes today, skip sending

    summary_text = generate_summary(notes)

    # Send summary
    await app.bot.send_message(chat_id=ALLOWED_USER_ID, text=summary_text)

    # Mark notes as summarized
    note_ids = [note.id for note in notes]
    db.mark_notes_as_summarized(note_ids)

    # Save summary to history
    db.save_daily_summary(summary_text, len(notes))


def setup_scheduler(app: Application):
    """Set up the daily summary scheduler."""
    hour, minute = SUMMARY_TIME.split(":")

    scheduler.add_job(
        send_daily_summary,
        trigger=CronTrigger(hour=int(hour), minute=int(minute)),
        args=[app],
        id="daily_summary",
        replace_existing=True,
    )

    scheduler.start()


def shutdown_scheduler():
    """Shut down the scheduler."""
    if scheduler.running:
        scheduler.shutdown()
```

**Step 2: Commit**

```bash
git add bot/scheduler.py
git commit -m "feat: add APScheduler for daily summaries"
```

---

### Task 8: Main Entry Point

**Files:**
- Create: `bot/main.py`

**Step 1: Create bot/main.py**

```python
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN
from bot.handlers import (
    start_command,
    summary_command,
    yesterday_command,
    status_command,
    settime_command,
    handle_voice,
)
from bot.scheduler import setup_scheduler, shutdown_scheduler

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")

    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("summary", summary_command))
    app.add_handler(CommandHandler("yesterday", yesterday_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("settime", settime_command))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Set up scheduler
    setup_scheduler(app)

    # Run bot
    logger.info("Starting Brain Dump Bot...")
    try:
        app.run_polling(allowed_updates=["message"])
    finally:
        shutdown_scheduler()


if __name__ == "__main__":
    main()
```

**Step 2: Commit**

```bash
git add bot/main.py
git commit -m "feat: add main entry point"
```

---

### Task 9: Create README

**Files:**
- Create: `README.md`

**Step 1: Create README.md**

```markdown
# Brain Dump Bot

A Telegram bot that captures voice notes throughout the day, transcribes them using Google Speech-to-Text, categorizes them with AI, and sends daily summaries.

## Features

- Voice note transcription via Google Speech-to-Text
- AI-powered categorization (Career, Health, Relationships, Finance, Learning, Projects)
- Daily summary at configurable time
- On-demand summary with `/summary`

## Setup

### Prerequisites

- Python 3.11+
- ffmpeg (for audio processing)
- Google Cloud account with Speech-to-Text API enabled
- OpenAI API key
- Telegram bot token (from @BotFather)

### Installation

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your credentials
5. Run the bot:
   ```bash
   python -m bot.main
   ```

## Commands

- `/start` - Welcome message and usage info
- `/summary` - Get today's summary
- `/yesterday` - Get yesterday's summary
- `/status` - Show today's note count
- `/settime HH:MM` - Change daily summary time

## Deployment

See deployment section in `docs/plans/2026-03-06-brain-dump-bot-design.md`
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README"
```

---

### Task 10: Test the Bot Locally

**Step 1: Create .env file with your credentials**

Copy `.env.example` to `.env` and fill in:
- `TELEGRAM_BOT_TOKEN` - Get from @BotFather
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to your service account JSON
- `OPENAI_API_KEY` - Your OpenAI key
- `ALLOWED_USER_ID` - Your Telegram user ID (get from @userinfobot)

**Step 2: Create and activate virtual environment**

```bash
cd ~/projects/brain-dump-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Step 3: Run the bot**

```bash
python -m bot.main
```

**Step 4: Test in Telegram**

1. Send `/start` to your bot
2. Send a voice note
3. Verify transcription and categorization
4. Send `/summary` to see the summary
5. Send `/status` to check stats

**Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete brain dump bot v1.0"
```
