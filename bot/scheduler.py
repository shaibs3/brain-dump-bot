from datetime import date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application

from bot.summary import generate_summary
from config import ALLOWED_USER_ID, SUMMARY_TIME, TIMEZONE
from db.models import Database

db = Database()
scheduler: AsyncIOScheduler | None = None


async def send_daily_summary(app: Application) -> None:
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


def setup_scheduler(app: Application) -> None:
    """Set up the daily summary scheduler."""
    global scheduler

    # Get summary time from settings or use default
    summary_time = db.get_setting("summary_time", SUMMARY_TIME) or SUMMARY_TIME
    hour, minute = summary_time.split(":")

    scheduler = AsyncIOScheduler(timezone=TIMEZONE)

    scheduler.add_job(
        send_daily_summary,
        trigger=CronTrigger(hour=int(hour), minute=int(minute)),
        args=[app],
        id="daily_summary",
        replace_existing=True,
    )

    scheduler.start()


def shutdown_scheduler() -> None:
    """Shut down the scheduler."""
    global scheduler
    if scheduler is not None and scheduler.running:
        scheduler.shutdown()
