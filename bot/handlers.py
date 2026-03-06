import os
import tempfile
from collections.abc import Callable, Coroutine
from datetime import date, timedelta
from functools import wraps
from typing import Any

from telegram import Update
from telegram.ext import ContextTypes

from bot.categorize import categorize_note
from bot.summary import generate_summary
from bot.transcribe import transcribe_audio
from config import ALLOWED_USER_ID, CATEGORY_EMOJIS
from db.models import Database

db = Database()


def authorized_only(
    func: Callable[..., Coroutine[Any, Any, None]],
) -> Callable[..., Coroutine[Any, Any, None]]:
    """Decorator to restrict bot to authorized user only."""

    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_user is None:
            return
        if ALLOWED_USER_ID and update.effective_user.id != ALLOWED_USER_ID:
            if update.message:
                await update.message.reply_text("⛔ Unauthorized")
            return
        return await func(update, context)

    return wrapper


@authorized_only
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    if update.message is None:
        return
    await update.message.reply_text(
        "🧠 Brain Dump Bot\n\n"
        "Send me voice notes throughout the day. I'll transcribe, categorize, "
        "and send you a daily summary.\n\n"
        "Commands:\n"
        "/summary - Get today's summary\n"
        "/yesterday - Get yesterday's summary\n"
        "/status - See today's stats\n"
        "/settime HH:MM - Change summary time"
    )


@authorized_only
async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /summary command - show today's notes."""
    if update.message is None:
        return
    notes = db.get_all_notes_for_date(date.today())
    summary_text = generate_summary(notes)
    await update.message.reply_text(summary_text)


@authorized_only
async def yesterday_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /yesterday command."""
    if update.message is None:
        return
    yesterday = date.today() - timedelta(days=1)
    notes = db.get_all_notes_for_date(yesterday)
    summary_text = generate_summary(notes, yesterday)
    await update.message.reply_text(summary_text)


@authorized_only
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /status command."""
    if update.message is None:
        return
    count = db.get_today_notes_count()
    last_time = db.get_last_note_time()

    if count == 0:
        await update.message.reply_text("📊 No notes recorded today yet.")
    else:
        last_str = last_time.strftime("%H:%M") if last_time else "unknown"
        await update.message.reply_text(
            f"📊 Today's Stats\n\nNotes: {count}\nLast note: {last_str}"
        )


@authorized_only
async def settime_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /settime command."""
    if update.message is None:
        return
    if not context.args:
        current = db.get_setting("summary_time", "21:00")
        await update.message.reply_text(
            f"Current summary time: {current}\nUsage: /settime HH:MM (e.g., /settime 21:00)"
        )
        return

    time_str = context.args[0]
    try:
        # Validate format
        hours, minutes = time_str.split(":")
        if not (0 <= int(hours) <= 23 and 0 <= int(minutes) <= 59):
            raise ValueError("Invalid time range")

        db.set_setting("summary_time", time_str)
        await update.message.reply_text(f"✅ Summary time set to {time_str}")
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Invalid format. Use HH:MM (e.g., 21:00)")


@authorized_only
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming voice notes."""
    if update.message is None or update.message.voice is None:
        return

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
        await processing_msg.edit_text(f"❌ Error: {e!s}")
