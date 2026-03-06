import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot.handlers import (
    handle_voice,
    settime_command,
    start_command,
    status_command,
    summary_command,
    yesterday_command,
)
from bot.scheduler import setup_scheduler, shutdown_scheduler
from config import TELEGRAM_BOT_TOKEN

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")

    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("summary", summary_command))
    app.add_handler(CommandHandler("yesterday", yesterday_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("settime", settime_command))

    # Add voice message handler
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Set up scheduler for daily summaries
    setup_scheduler(app)

    # Run bot
    logger.info("Starting Brain Dump Bot...")
    try:
        app.run_polling(allowed_updates=["message"])
    finally:
        shutdown_scheduler()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    main()
